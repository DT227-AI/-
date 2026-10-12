#!/usr/bin/env python3
"""Validate agent-authored analysis and atomically archive captured WeChat text."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING = {'scene', 'srcid', 'from', 'share_token', 'isappinstalled'}


def canonical_url(url):
    if not isinstance(url, str):
        raise ValueError('url must be a string')
    p = urlsplit(url)
    if (p.scheme != 'https' or p.hostname != 'mp.weixin.qq.com' or
            p.username or p.password or p.port not in (None, 443) or
            not (p.path == '/s' or p.path.startswith('/s/'))):
        raise ValueError('Expected an HTTPS mp.weixin.qq.com article URL')
    query = sorted((k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                   if k not in TRACKING)
    return urlunsplit(('https', 'mp.weixin.qq.com', p.path, urlencode(query), ''))


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Input must be an object')
    allowed = {'url', 'title', 'account', 'published_at', 'status', 'source_method',
               'body', 'overview', 'main_content', 'key_viewpoints', 'limitations'}
    if set(data) - allowed:
        raise ValueError('Unknown input fields: ' + ', '.join(sorted(set(data) - allowed)))
    result = {k: data.get(k) for k in allowed}
    result['canonical_url'] = canonical_url(data.get('url'))
    for key in ('title', 'account', 'published_at'):
        if result[key] is not None and not isinstance(result[key], str):
            raise ValueError(key + ' must be text or null')
    if result['status'] not in ('verified', 'partial', 'blocked'):
        raise ValueError('Invalid status')
    if result['source_method'] not in ('wechat_cli', 'web_fetch', 'browser', 'user_provided'):
        raise ValueError('Invalid source_method')
    body = result['body']
    if not isinstance(body, str):
        raise ValueError('body must be text')
    for key in ('main_content', 'key_viewpoints', 'limitations'):
        if not isinstance(result[key], list):
            raise ValueError(key + ' must be a list')
    if any(not isinstance(x, str) or not x.strip() for x in result['limitations']):
        raise ValueError('limitations must contain nonempty text')
    if result['status'] in ('partial', 'blocked') and not result['limitations']:
        raise ValueError('Incomplete capture requires limitations')
    if result['status'] == 'blocked':
        if body or result['overview'] or result['main_content'] or result['key_viewpoints']:
            raise ValueError('Blocked capture cannot contain body or analysis')
        return result
    if not body.strip() or not result['main_content']:
        raise ValueError('Readable capture requires body and main_content')
    if not result['key_viewpoints'] and not result['limitations']:
        raise ValueError('Explain absence of viewpoints in limitations')
    items = [result['overview']] + result['main_content'] + result['key_viewpoints']
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('text'), str) or not item['text'].strip():
            raise ValueError('Each analysis item requires text')
        if set(item) - {'text', 'evidence', 'kind'}:
            raise ValueError('Unknown analysis item fields')
        quotes = item.get('evidence')
        if not isinstance(quotes, list) or not quotes:
            raise ValueError('Each analysis item requires evidence')
        if any(not isinstance(q, str) or not q.strip() or q not in body for q in quotes):
            raise ValueError('Evidence must be an exact nonempty body excerpt')
    for item in result['key_viewpoints']:
        if item.get('kind') not in ('author_claim', 'reported_opinion', 'agent_inference'):
            raise ValueError('Viewpoints require a valid kind')
    if result['status'] == 'partial' and not result['overview']['text'].startswith('仅基于已获取片段'):
        raise ValueError('Partial overview must disclose partial coverage')
    return result


def render(data):
    lines = ['# ' + (data['title'] or '标题未知'), '',
             '- 原文：' + data['url'], '- 公众号：' + (data['account'] or '未知'),
             '- 发布时间：' + (data['published_at'] or '未知'),
             '- 存档时间（UTC）：' + data['captured_at'],
             '- 状态：' + data['status'], '- 获取方式：' + data['source_method'], '']
    for title, items in [('内容概述', [data['overview']] if data['overview'] else []),
                         ('主要内容', data['main_content']), ('核心观点', data['key_viewpoints'])]:
        lines += ['## ' + title, '']
        if not items:
            lines += ['无可核验内容或明确观点，见限制说明。', '']
        for item in items:
            kind = {'author_claim': '作者观点', 'reported_opinion': '文中转述观点',
                    'agent_inference': '分析推断'}.get(item.get('kind'))
            lines += ['- ' + (('【' + kind + '】') if kind else '') + item['text']]
            for quote in item['evidence']:
                lines += ['', *['  > ' + x for x in quote.splitlines()]]
            lines += ['']
    lines += ['## 限制说明', ''] + ['- ' + x for x in data['limitations']]
    lines += ['', '## 已获取正文', '', data['body'] or '正文未获取。', '']
    return '\n'.join(lines)


def archive(data, output):
    data = validate(data)
    article_dir = Path(output).resolve() / digest(data['canonical_url'])
    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True)
    revision = digest(serialized)
    target = article_dir / revision
    article_dir.mkdir(parents=True, exist_ok=True)
    reused = target.exists()
    if not reused:
        data['captured_at'] = datetime.now(timezone.utc).isoformat()
        data['body_sha256'] = digest(data['body'])
        data['schema_version'] = 1
        temporary = Path(tempfile.mkdtemp(prefix='.pending-', dir=article_dir))
        try:
            (temporary / 'manifest.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            (temporary / 'article.md').write_text(render(data), encoding='utf-8')
            try:
                os.rename(temporary, target)
            except OSError:
                if not target.is_dir():
                    raise
                reused = True
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    # Detect damaged existing archives instead of reporting a successful reuse.
    if not (target / 'manifest.json').is_file() or not (target / 'article.md').is_file():
        raise ValueError('Existing revision is incomplete; inspect it before retrying')
    return {'archive': str(target / 'article.md'), 'manifest': str(target / 'manifest.json'), 'reused': reused}


def lookup(url, output):
    directory = Path(output).resolve() / digest(canonical_url(url))
    versions = []
    for path in directory.glob('*/manifest.json'):
        if path.parent.name.startswith('.'):
            continue
        data = json.loads(path.read_text(encoding='utf-8'))
        versions.append({'manifest': str(path), 'archive': str(path.with_name('article.md')),
                         'status': data['status'], 'captured_at': data['captured_at']})
    return sorted(versions, key=lambda x: x['captured_at'], reverse=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--input', type=Path)
    source.add_argument('--lookup')
    parser.add_argument('--output', type=Path, default=Path('wechat-archives'))
    args = parser.parse_args()
    try:
        result = (lookup(args.lookup, args.output) if args.lookup else
                  archive(json.loads(args.input.read_text(encoding='utf-8')), args.output))
    except (ValueError, OSError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())

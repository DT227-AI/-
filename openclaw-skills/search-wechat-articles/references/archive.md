# Archive with main content and viewpoints

When asked to archive, create both a readable Markdown artifact and JSON manifest using the bundled Python 3 standard-library script. No extra package or API key is required. Text is archived locally; linked images are not downloaded by this script.

## Analyze the captured body

Read the entire captured body. Produce a concise overview (typically 150–300 Chinese characters), 3–7 main-content items and 3–5 core viewpoints when supported; use fewer for short articles. Do not pad the count. Each overview/content/viewpoint item has a `text` and a nonempty `evidence` list of short exact body excerpts. Keep evidence minimal while enough to locate the support. The script checks exact presence; the agent must check semantic support.

Distinguish reported facts, attributed opinions, and agent inferences. For viewpoints include `kind`: `author_claim`, `reported_opinion`, or `agent_inference`. Preserve qualifiers, scope, units, dates and attribution. Never turn the author's projections into established facts. If there is no clear viewpoint, use an empty list and explain why in `limitations`. Do not create summaries from snippets or failed fetches.

For `partial`, prefix the overview with “仅基于已获取片段” and list missing sections. For `blocked`, body and analysis must be empty: archive the link, failure reason and status only. Never call that a full-text archive.

## Input

Write UTF-8 JSON with these fields (paths passed to the command may be absolute):

```json
{
  "url": "https://mp.weixin.qq.com/s/example",
  "title": "示例标题",
  "account": null,
  "published_at": null,
  "status": "verified",
  "source_method": "user_provided",
  "body": "企业计划明年扩大研发团队。该计划尚待审批。",
  "overview": {"text": "文章介绍一项尚待审批的研发扩充计划。", "evidence": ["企业计划明年扩大研发团队。", "该计划尚待审批。"]},
  "main_content": [{"text": "计划明年扩充研发团队。", "evidence": ["企业计划明年扩大研发团队。"]}],
  "key_viewpoints": [],
  "limitations": ["没有明确的评论性观点。", "用户提供正文，原链接未独立核验；未下载图片。"]
}
```

Allowed methods: `wechat_cli`, `web_fetch`, `browser`, `user_provided`. Use the method that actually supplied the body; a reused archive keeps its original provenance. `verified` for user-provided text describes checking that copy only, not verifying the live URL. Unknown metadata uses null. Do not put cookies, tokens, browser profiles or request headers in the input.

```bash
python3 scripts/archive_article.py --input /path/article.json --output /path/wechat-archives
python3 scripts/archive_article.py --lookup 'https://mp.weixin.qq.com/s/example' --output /path/wechat-archives
```

Output is one JSON result with absolute `archive` and `manifest` paths and `reused`. Stable article-ID and revision-ID directories avoid unsafe title filenames. Identical inputs reuse a revision; changed text/analysis/status create a new revision without overwriting previous captures. `captured_at` is archive creation time in UTC; `published_at` remains the supplied publication time. Lookup returns all captured versions, including failures: prefer a suitable verified version rather than the latest blocked attempt. Read back the generated Markdown before delivery to verify completeness and analysis quality. Return file links plus a concise digest and limitations.

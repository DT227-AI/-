import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('archive_article', Path(__file__).resolve().parents[1] / 'scripts/archive_article.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def fixture():
    return dict(url='https://mp.weixin.qq.com/s/example', title='../中文标题', account=None,
                published_at=None, status='verified', source_method='user_provided',
                body='企业计划扩大研发。计划尚待审批。',
                overview={'text': '研发扩充计划尚待审批。', 'evidence': ['计划尚待审批。']},
                main_content=[{'text': '企业计划扩大研发。', 'evidence': ['企业计划扩大研发。']}],
                key_viewpoints=[], limitations=['未独立核验原链接；没有明确观点；图片未存档。'])


class ArchiveTests(unittest.TestCase):
    def test_roundtrip_reuse_revision_lookup(self):
        with tempfile.TemporaryDirectory() as root:
            data = fixture()
            first = a.archive(data, root)
            self.assertFalse(first['reused'])
            self.assertTrue(a.archive(data, root)['reused'])
            self.assertEqual(json.loads(Path(first['manifest']).read_text())['body'], data['body'])
            self.assertIn('计划尚待审批。', Path(first['archive']).read_text())
            self.assertTrue(Path(first['archive']).is_relative_to(Path(root).resolve()))
            data['body'] += '后续更新。'
            second = a.archive(data, root)
            self.assertNotEqual(first['archive'], second['archive'])
            self.assertTrue(Path(first['archive']).exists())
            self.assertEqual(len(a.lookup(data['url'], root)), 2)

    def test_evidence_fabrication_rejected(self):
        data = fixture()
        data['overview']['evidence'] = ['审批已经完成。']
        with self.assertRaises(ValueError):
            a.validate(data)

    def test_blocked_never_summarized(self):
        data = fixture()
        data['status'] = 'blocked'
        with self.assertRaises(ValueError):
            a.validate(data)
        data.update(body='', overview=None, main_content=[], key_viewpoints=[])
        self.assertEqual(a.validate(data)['status'], 'blocked')

    def test_partial_disclosed(self):
        data = fixture()
        data['status'] = 'partial'
        with self.assertRaises(ValueError):
            a.validate(data)
        data['overview']['text'] = '仅基于已获取片段：研发计划待审批。'
        a.validate(data)

    def test_url_identity_and_rejection(self):
        base = 'https://mp.weixin.qq.com/s?__biz=abc&mid=1&idx=2&sn=xyz'
        self.assertEqual(a.canonical_url(base), a.canonical_url(base + '&scene=1#fragment'))
        self.assertNotEqual(a.canonical_url(base), a.canonical_url(base.replace('mid=1', 'mid=2')))
        for url in ['https://mp.weixin.qq.com.evil/s/a', 'https://user:secret@mp.weixin.qq.com/s/a', 'file:///s/a']:
            with self.assertRaises(ValueError):
                a.canonical_url(url)

    def test_viewpoint_attribution(self):
        data = fixture()
        data['key_viewpoints'] = [copy.deepcopy(data['overview'])]
        with self.assertRaises(ValueError):
            a.validate(data)
        data['key_viewpoints'][0]['kind'] = 'agent_inference'
        a.validate(data)


if __name__ == '__main__':
    unittest.main()

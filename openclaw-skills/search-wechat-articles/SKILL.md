---
name: search-wechat-articles
description: Search, verify, filter, and summarize public WeChat Official Account articles from mp.weixin.qq.com. Use when the user asks to 搜索微信公众号文章、查某个公众号写过什么、按主题或时间找微信文章、整理公众号资料、查找公众号原文链接、批量摘要微信公众号内容, compare coverage across public accounts, or archive 微信文章 with 主要内容、核心观点 and source evidence.
---

# Search WeChat Articles

Search public WeChat Official Account articles and return traceable source links. Treat search snippets as discovery evidence only; verify article content before summarizing it.

## Workflow

1. Parse the request into:
   - topic and optional exact phrases;
   - optional account name;
   - optional date range;
   - desired result count, default 10;
   - whether the user wants links only, summaries, synthesis, or local archives;
   - archive directory if specified; otherwise use `./wechat-archives` in the current workspace when archiving is requested. Direct article links skip discovery and go straight to verification.

2. Build a source-priority plan:
   - first, any account explicitly requested by the user;
   - then the default priority accounts listed below;
   - finally, other relevant public accounts for broader coverage.

3. Run several `web_search` queries instead of relying on one query. Read [references/search-patterns.md](references/search-patterns.md). For broad topic discovery, run one query per default priority account containing both its display name and WeChat ID, then up to three broader variants as needed. For account-specific requests, search only the requested accounts unless expansion is needed and disclosed. Stop querying a provider when it returns a challenge or rate limit; report incomplete coverage. Do not report a priority account as searched unless its dedicated query was actually executed.

4. Keep results whose final or displayed URL belongs to `mp.weixin.qq.com`. Results from other sites may help discover titles but are not valid article sources.

5. Deduplicate results by normalized WeChat URL and near-identical title. Prefer:
   - direct `mp.weixin.qq.com/s/...` or `/s?__biz=...` links;
   - results matching an account explicitly requested by the user;
   - verified results from the default priority accounts;
   - results inside the requested date range;
   - pages whose title and snippet both match the topic.

6. Verify the leading results using [references/retrieval.md](references/retrieval.md). Reuse a verified local archive or this run's captured body first. Check for `wechat-article` / `wechat-article-to-markdown` and read its actual help before invoking it; never invent CLI flags. If unavailable, use one public fetch, then browser extraction only when appropriate. Detect challenge pages even with HTTP 200. Respect cooldowns and stop conditions rather than repeatedly fetching blocked URLs.

7. Never infer author, account, publication date, or article claims from the URL alone. Use article metadata or label the field unknown.

8. Present concise results with:
   - article title;
   - official account name, when verified;
   - publication date, when verified;
   - one-sentence relevance note or summary;
   - direct WeChat article link;
   - verification status.

9. When archiving is requested, always extract **主要内容** and **核心观点** along with the body. Read [references/archive.md](references/archive.md), prepare evidence-backed analysis, and run `scripts/archive_article.py`. It writes a readable Markdown archive and a structured JSON manifest without an LLM API dependency. The calling agent performs the analysis; the script validates evidence and writes files. A links-only search does not automatically archive.

## Default Priority Accounts

Search these sources before expanding to other accounts:

| Priority | Account | WeChat ID |
|---|---|---|
| 1 | 投资界 | `pedaily2012` |
| 2 | 36氪 | `wow36kr` |
| 3 | 投中网 | `China-Venture` |
| 4 | 融中财经 | `thecapital` |
| 5 | 创投日报 | `VentureCapitalDaily` |

Treat the account name and WeChat ID as aliases for the same preferred source. Verify the publisher from article metadata because search snippets can misattribute reposts. Priority affects search order and ranking, but relevance and source verification remain mandatory.

## Search Modes

### Topic search

Search broadly, then add synonyms, industry terms, company names, product names, and exact phrases. Use the current year only when freshness matters.

### Account-specific search

Combine the quoted account name with the topic and `site:mp.weixin.qq.com`. Do not claim that a result belongs to the account until the article metadata confirms it.

### Recent articles

Include the current year and recent month names in query variants. Search-engine dates are hints; verify dates from the article.

### Content synthesis

Verify and fetch the selected articles first. Separate:

- statements supported by article text;
- conclusions synthesized across articles;
- unresolved conflicts or inaccessible sources.

## Output Format

Use a Markdown table when returning multiple results:

| # | 标题 | 公众号 | 日期 | 相关性/摘要 | 状态 | 链接 |
|---|---|---|---|---|---|---|

For requested archives, also give local archive links, content status (`verified` / `partial` / `blocked`), and a short main-content/key-viewpoint digest. Treat archived pages as a captured version, not a guarantee of current availability.

After the table, add a short `检索说明` listing the query scope, result count, priority-account coverage, and any access limitations. Explicitly state which priority accounts returned verified matches and which did not.

## Guardrails

- Search only publicly accessible content. Do not bypass login, paywalls, captchas, access controls, or deleted/private article restrictions.
- Do not present third-party reposts as the original WeChat source.
- Do not fabricate results when search coverage is weak. Say what was searched and ask for an account name, title fragment, or known link when that would materially improve recall.
- Preserve direct source links in every research or summary output.

# Retrieval and access failures

These are agent workflow rules, not a promise that an extractor defeats WeChat restrictions. No stealth browsers, IP/proxy rotation, CAPTCHA solving, borrowed cookies, or credential extraction.

## Reuse first

- Normalize only for deduplication; use the original discovered URL to retrieve (query parameters may be needed). Preserve `__biz`, `mid`, `idx`, `sn`, and unknown parameters; remove only known tracking parameters and fragments.
- If an archive directory exists, use `python3 scripts/archive_article.py --lookup URL --output DIRECTORY` to list captured versions and their status. Read the returned manifest/body and check title, publisher, completeness, and capture date. Reuse for the same article unless freshness or a new version is requested; disclose the capture date.
- Keep one result per URL per run, including failures, and a host/provider cooldown ledger in task state. Capture the first successful tool output directly for analysis and archiving; do not fetch it again just to save it.

## Bounded retrieval

1. Check `command -v wechat-article` and `command -v wechat-article-to-markdown`, or inspect the available skill of that name. Read the installed tool's help and dependency instructions. Use only a documented public retrieval mode. Missing tools are a fallback condition, not a reason to install arbitrary packages automatically.
2. If no specialist tool is available, use a public article fetch tool once. Never run both after a successful complete extraction.
3. For an ordinary parsing/JavaScript-rendering failure, use a normal browser session once if available. Inspect the actual page and extract only visible article content; do not classify the tool's success flag as proof of success. Browser tool unavailable: retain the discovered link and report the limitation.
4. On CAPTCHA, verification/interstitial text, `环境异常`, `访问过于频繁`, `安全验证`, login/access restriction, HTTP 401/403/429: stop automated requests to that host for this run. A specialist tool's verification error has the same meaning. Do not cycle tools to evade the restriction. Honor `Retry-After` if present; otherwise note a cooldown of at least 15 minutes before a later user-triggered attempt. Do not auto-schedule retries.
5. Timeout or 5xx without a challenge: at most one retry after at least 5 seconds. If it still fails, stop that URL. Deleted/private/unavailable article: no retry. Per URL, cap automatic retrieval attempts at three total (including retry/browser). Serial retrieval, with at least 3 seconds between article requests to the same host; never batch parallel requests. A challenge stops the whole host, not only that URL.
6. A user can complete a verification themselves in their browser and explicitly request resumption. Otherwise offer a user-provided copy/export or pasted body as the recovery path. Label that source `user_provided`, and keep original-link verification unknown if it was not verified. Search snippets and third-party reposts cannot stand in for verified original text.

## Content verification

A 200 response may be an anti-bot page. Inspect title, publisher/date metadata when present, and a coherent article body (often `js_content`); exclude navigation, challenge text and recommendations. Do not use a fixed minimum character count: short announcements can be valid. Missing body, truncation, missing image-only sections, or inaccessible charts must be reported. If only part of the body is available, use `partial` and summarize only that portion, with explicit gaps. `verified` means the captured article text was checked, not that its claims are independently true.

Preserve unknown title/publisher/date as unknown. Keep capture time separate from publication time. Remote image links are not offline image archives; record image limitations and do not silently claim full offline preservation.

# Search Patterns

Replace placeholders and run multiple complementary queries.

## General topic

```text
site:mp.weixin.qq.com "<topic>"
site:mp.weixin.qq.com "<exact phrase>"
site:mp.weixin.qq.com "<topic>" 微信公众号
site:mp.weixin.qq.com "<topic synonym>" "<related entity>"
```

## Specific account

```text
site:mp.weixin.qq.com "<account name>" "<topic>"
site:mp.weixin.qq.com "<account name>" "<exact phrase>"
site:mp.weixin.qq.com "<account name>" <year>
```

## Recent coverage

```text
site:mp.weixin.qq.com "<topic>" <current year>
site:mp.weixin.qq.com "<topic>" <current year> <current month>
site:mp.weixin.qq.com "<topic>" 最新
```

## Companies, people, and products

```text
site:mp.weixin.qq.com "<entity full name>"
site:mp.weixin.qq.com "<entity abbreviation>" "<industry>"
site:mp.weixin.qq.com "<person>" "<organization>"
site:mp.weixin.qq.com "<product>" 发布 OR 评测 OR 分析
```

## Recall fallback

If direct domain search finds too little:

1. Search the exact title fragment without a site restriction.
2. Search the topic with `微信公众平台` or `公众号文章`.
3. Use the browser to search Sogou Weixin article search when available.
4. Accept a result only after resolving it to a direct `mp.weixin.qq.com` article URL.

## URL normalization

For deduplication:

- lowercase the hostname;
- remove the fragment;
- remove obvious tracking parameters such as `scene`, `srcid`, `from`, and `share_token`;
- retain parameters required to identify the article, especially `__biz`, `mid`, `idx`, and `sn`;
- treat a clean `/s/<id>` URL as canonical when available.

## Ranking

Rank each candidate using this order:

1. verified account-name match;
2. title exact-phrase match;
3. verified date-range match;
4. direct canonical WeChat URL;
5. body text available for verification;
6. snippet-only or inaccessible result.

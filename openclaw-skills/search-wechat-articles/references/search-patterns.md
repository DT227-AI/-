# Search Patterns

Replace placeholders and run multiple complementary queries.

## Default priority accounts

For broad topic discovery, use this five-query priority pass. Skip it for direct links or searches restricted to named accounts. Stop the affected provider if it is rate-limited or challenged; never claim an unexecuted query was searched. Each query includes both aliases:

```text
site:mp.weixin.qq.com ("投资界" OR "pedaily2012") "<topic>"
site:mp.weixin.qq.com ("36氪" OR "wow36kr") "<topic>"
site:mp.weixin.qq.com ("投中网" OR "China-Venture") "<topic>"
site:mp.weixin.qq.com ("融中财经" OR "thecapital") "<topic>"
site:mp.weixin.qq.com ("创投日报" OR "VentureCapitalDaily") "<topic>"
```

If the user explicitly names another account, search that account before this default list.
Do not mark a priority account as searched unless its dedicated query was executed.

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
3. Optionally use normal Sogou Weixin article search in the browser when available. If challenged, stop that provider; do not repeatedly refresh or use it to route around a WeChat access restriction.
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

1. verified match to an account explicitly requested by the user;
2. title exact-phrase and topical relevance;
3. verified match to a default priority account;
4. verified date-range match;
5. direct canonical WeChat URL;
6. body text available for verification;
7. snippet-only or inaccessible result.

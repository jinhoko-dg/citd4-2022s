# Crawling Sequence

\* let `N` be #shares in total market ( `N` is around 2500)

### Past data crawl sequence

#### Crawl

idx | query content | # reqs. | action
----|---------------|---------|-------
1 | [12001] 전종목시세 | 1 | add candles to `prices`, `daily_meta`
2 | [12009] 투자자별 거래실적(개별종목) | N | add to `daily_trades_per_subject`
3 | [12023] 외국인보유량(개별종목) | 1 | add to `daily_foreigner_hold`
4 | [32001] 개별종목 공매도 거래 | 3 | add to `daily_short`
5 | [33001] 개별종목 공매도 잔고 | 3 | add to `daily_short`
6 | [12021] PER/PBR/배당수익률(개별종목) | 1 | add to `daily_value`


### Present data crawl sequence


#### Crawl

#### Post-crawl

- update table `meta` (`주식` only)
- update table `adjusted_prices` when necessary

# Schema Design

- postgresql
- https://www.postgresql.org/docs/current/datatype-numeric.html


## DB `adjusted_krx`

### Adjustment guide


When there's a change, what remains the same is factors that change are as following : 
- price
- volume

Especially, eps, bps, and div_ps are also affected.

What is not adjusted
- trading value
- ratio / rate
- per/pbr/yield rate

## DB `krx`

### table `prices`

attr|type|example or memo
---|---|--|
!timestamp | time | 9223372036854775806 ( in utc. if 1d, record as 00:00(of local time), if 1m, 00:00:00 of sunday, if monthly 00:00:00 of day 1, and so on )
!ticker | string | '005930'
!time_unit | string | '1S' / '1M' / '1H' / '1d' / '1w' / '1m' ...
open | int | 90000
high | int | 90001
low | int | 90002
close | int | 90003
volume | int | 1000000 (# stocks)


### table `adjusted_prices`
(same with table `prices`)
ohlcv should be adjusted pre-existing ohlcv values may be updated.

### table `daily_trade_meta`

Do not need adjustment for these data. Although trade_volume is duplicated, it is worth it. This table itself does NOT need to be adjusted.

attr|type|example or memo
---|---|--|
!ticker | string | '005930'
!timestamp | time | 9223372036854775806 (in utc. 00:00 of that day (in local time) )
trade_volume | int | 거래량
trade_value | int | 거래대금
market_cap | int | 시가총액 
total_shares | int | 상장주식수 
delta | float | delta percent compared to yesterday. if delta is strange, it means now is the point of price adjusting

### table `daily_trades_per_subject`

attr|type|example or memo
---|---|--|
!ticker | string | '005930'
!timestamp | time | 9223372036854775806 (in utc. 00:00 of that day (in local time) )
fiin_sell_vol | int
fiin_buy_vol |  int
fiin_netbuy_vol | int
fiin_sell_value | int
fiin_buy_value | int
fiin_netbuy_value | int
insr_........
net_all_.....

(total 13 * 6 columns + 2)

### table `daily_foreigner_hold`

attr|type|example or memo
---|---|--|
!ticker | string | '005930'
!timestamp | time | 9223372036854775806 (in utc. 00:00 of that day (in local time) )
foreigner_hold_vol | int | 외인보유수량
foreigner_hold_rate | float | 외인지분율
foreigner_limit_vol | int | 외인한도수량
foreigner_limit_consumption_rate | float | 외인한도소진율

*consump_rate is equivalent hold_vol / limit_vol*


### table `daily_short`

attr|type|example or memo
---|---|--|
!ticker | string | '005930'
!timestamp | time | 9223372036854775806 (in utc. 00:00 of that day (in local time) )
short_volume | int | 공매도 거래량
short_value | int | 공매도 거래대금
short_balance_volume | int | 공매도잔고수량
short_balance_value | int | 공매도잔고금액

*when joined with volume/ratio from prices/prices-meta table, one can get short ratio*


### table `daily_value`

attr|type|example or memo
---|---|--|
!ticker | string | '005930'
!timestamp | time | 9223372036854775806 (in utc. 00:00 of that day (in local time) )
eps | float | XXXX if not available
per | float | XXXX if not available
bps | float | XXXX if not available
pbr | float | XXXX if not available
dividend_per_share | int | 주당배당금
dividend_yield | float | 주당수익률 

### table `meta`

\* this table does not hold previous history 
TODO add delisted shares (maybe?)

\* 상장회사 상세검색12020 + 전종목기본정보12005

* 일반 주식은 보통주이면서 주권주여야 함. + in kospi + kosdaq

attr|type|example or memo
---|---|--|
ticker | string | '005930'
standard_ticker | string | 'KR7005930003'
name_kor | string | '삼성전자'
name_eng | string | 'SamsungElectronics'
!market | string | 'KOSPI' 'KOSDAQ' 'KONEX'
!is_certificate | bool | 주권인 경우만 true
!stock_type | string | '종류주권' '신형우선주' '보통주' '구형우선주'
department | string | 소속부
is_listed | bool
listing_date | datetime | 
delisting_date | datetime | 0 if is_listed == False

(TODO later)
업종구분 | string | '건설업' '' if not exists

### table `daily_index_prices`

cols : time(datetime), ticker(vc16), open(real), high(real), low(real), close(real), value(bigint), volume(bigint), market_cap(bigint)


### table `daily_index_constituents`

// TODO 11006 지수구성종목

## table `index_meta`

// stock.get_index_ticker_name

cols : ticker(int), base_date(datetime), release_date(datetime), base_index(real)


# TODO write for indexes

## TODO tables to add later

### table `tradibility_status`
종목정보 > 전종목 지정내역

### table `daily_block_deal`
거래실적 > 대량매매

### table `group_cluster`
이슈통계 > 기업집단 df

### table `short`
통계 > 공매도통계


### and so on...
- etf, etn pricing
- gold / emission rights/ oil pricing
- derivatives(futures, ..) pricing 
- bond pricing
- eurex pricing
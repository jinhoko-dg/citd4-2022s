

from db import DB

db = DB()
db.connect()

import datetime

sector_idx_price_q = f"""
    select * from 
			(select
				time, close, open, high, low
			from prices
			where
				ticker = '005930'
				and time <= '2021-01-01'
			order by time desc
			limit 100) as f
		order by time asc
"""

data = db.query(sector_idx_price_q)

result = ""
for d in data:
    tmp = ""
    for cnt, it in enumerate(d):
        if isinstance(it, datetime.datetime):
            it = it.strftime('%Y-%m-%d')

        if cnt != len(d)-1:
            tmp += '"' + str(it) + '",'
        else:
            tmp+= '"' + str(it) + '"\n'
    result += tmp


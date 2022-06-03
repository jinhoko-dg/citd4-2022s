import json
import tqdm
import yaml
import pickle
import sys
import logging
import random
import time

from pykrx.pykrx import stock
from pykrx.pykrx.website.krx.krx_proxy import Proxy

from concurrent.futures import ThreadPoolExecutor

#export YR=14; python3 crawl-index.py 20${YR}0101 20${YR}1231

# initialize proxy
with open('private.yaml') as f:
	private = yaml.load(f, Loader=yaml.FullLoader)
	token = private['PROXY_KEY']
assert token != ""

globalProxy = Proxy( firstInit = True )
globalProxy.generate_proxy_list(token)
globalProxy.set_enable_proxy(True)

test_proxy = globalProxy.get()
print(f"test_proxy : {test_proxy}")


CONCURRENCY = 100

"""
Crawl mainbody
"""

def indexCrawl(tickers, start_date:int, end_date:int):

	start_date = str(start_date)
	end_date = str(end_date)

	def crawl(ticker):
		df = stock.get_index_ohlcv_by_date(start_date, end_date, ticker)
		# if ohlev empty, just remove
		# empty df means no data
		if not df.empty:
			df = df[df.open != 0]
		return df
	
	with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
		dfs = list( pool.map( crawl, tickers ) )

	# postprocess
	result = {}
	for idx, t in enumerate(tickers):
		df = dfs[idx]
		# pass no result
		if not df.empty:
			result[t] = dfs[idx]
	
	return result


"""                                                                                   
Crawl past data
"""
seqno = random.randrange(1000,9999)

logging.basicConfig(filename='./tmp-index/exec.log'
					,format=f"[%(asctime)s][{seqno}][%(levelname)s] %(message)s"
					,level = logging.INFO)

logging.info("start program")

## parse input date range
start_date = int(sys.argv[1])
end_date = int(sys.argv[2])

assert start_date <= end_date
assert end_date - start_date <= 10000 #EG 20180101 - 20170101
logging.info(f"start_date {start_date} / end_date {end_date}")

## find lists
tickers = []
for market in ['KRX', 'KOSPI', 'KOSDAQ', '테마']:
	ts = stock.get_index_ticker_list(market=market)
	tickers += ts

logging.info(f"num_index_tickers : {len(tickers)}")

start = time.time()

try:
	result = indexCrawl(tickers, start_date, end_date)
	logging.info(f"crawl completed")
	logging.info(f"actual tickers in the period : {len(result.keys())}")

	# write
	with open(f'./tmp-index/{start_date}-{end_date}.pickle', 'wb') as f:
			pickle.dump(result, f)
	logging.info(f"write completed")
	
except BaseException as e:
	logging.error(f"crawl failed or write failed")
	print(e)

end = time.time()
logging.info(f"write success in : {int(end-start)}(s)")

logging.info("program terminated")

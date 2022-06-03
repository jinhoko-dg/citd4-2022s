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

INVESTOR_MAPPING = {
	'금융투자' : 'FIIN',
	'보험' : 'INSR',
	'투신' : 'INTR',
	'사모' : 'PRFD',
	'은행' : 'BANK',
	'기타금융' : 'ETCO', 		# added later
	'연기금 등' : 'PENF' ,
	'기관합계' : 'NET_ORGN',	# SUM of organization
	'기타법인' : 'ETCC',
	'개인' : 'INDV',
	'외국인' : 'FRGN',
	'기타외국인' : 'ETCF',
	'전체' : 'NET_ALL' 			# SUM of all investors
}

CONCURRENCY = 100

def dailyCrawl(date):

	"""
	step 1
	"""
	# get ohlcv prices
	#stock.register_proxy( current_proxy )
	df = stock.get_market_ohlcv_by_ticker(date, market="ALL")
	js = df.to_json(orient = 'index')
	daily_ohlcv = json.loads(js)
	tickers = list(daily_ohlcv.keys())

	print(f"	Num. tickers for date {date}: {len(tickers)}")
	# index = ticker
	# open   high    low  close   volume      amount  delta    market_cap  total_shares
	step1_df = df

	# # check if anything has 0 in ohlcv

	# FOR DEBUGGING
	#tickers = tickers[:10] # TODO delete

	# """
	# step 2
	# """
	def get_trades_investor( tup ):
		
		date = tup[0]
		ticker = tup[1]
		# print(date, ticker)

		#stock.register_proxy( proxy.getProxy() )
		df = stock.get_market_trading_value_and_volume_by_investor(date, date, ticker)
		js = df.to_json(orient = 'index')
		dd = json.loads(js)
		for kor_key in INVESTOR_MAPPING.keys():
			eng_key = INVESTOR_MAPPING[kor_key]
			dd[eng_key] = dd.pop(kor_key)
		# print(len(dd))
		return dd

	# TODO why error? WHY?
	with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
		date_ticker_tuples = [ (date, t) for t in tickers ]
		responses = list( pool.map( get_trades_investor, date_ticker_tuples ) )

	step2_results = responses

	"""
	step 3
	"""
	# daily foreigner hold
	# TODO day - 1 ; 장개시시점기준이기때문
	#stock.register_proxy( proxy.getProxy() )
	step3_df = stock.get_exhaustion_rates_of_foreign_investment_by_ticker(date, "ALL")

	"""
	step 4
	"""
	# short trade
	#stock.register_proxy( proxy.getProxy() )
	df_kpi = stock.get_shorting_value_and_volume_by_ticker(date, "KOSPI", ["주식"])
	df_kdq = stock.get_shorting_value_and_volume_by_ticker(date, "KOSDAQ", ["주식"])
	df_knx = stock.get_shorting_value_and_volume_by_ticker(date, "KONEX", ["주식"] )
	step4_1_df_3 = (df_kpi, df_kdq, df_knx)
	#print(len(df))
	# TODO assert sum(kospi, kdq, nex) = row of other table

	# TODO Day-2
	#short balance
	#stock.register_proxy( proxy.getProxy() )
	df_kpi = stock.get_shorting_balance_by_ticker(date, "KOSPI")
	df_kdq = stock.get_shorting_balance_by_ticker(date, "KOSDAQ")
	df_knx = stock.get_shorting_balance_by_ticker(date, "KONEX")
	step4_2_df_3 = (df_kpi, df_kdq, df_knx)
	#print(len(df))

	final_result = (step1_df, step2_results, step3_df, step4_1_df_3, step4_2_df_3)
	#print(final_result) # TODO delete
	return final_result


"""                                                                                   
Crawl past data
"""
seqno = random.randrange(1000,9999)

logging.basicConfig(filename='./tmp/exec.log'
					,format=f"[%(asctime)s][{seqno}][%(levelname)s] %(message)s"
					,level = logging.INFO)

logging.info("start program")

## parse input date range
start_date = int(sys.argv[1])
end_date = int(sys.argv[2])

assert start_date <= end_date
logging.info(f"start_date {start_date} / end_date {end_date}")

## find opening dates
try:
	dates_ts = stock.get_previous_business_days(fromdate= str(start_date), todate= str(end_date))
except:
	logging.info("problem occured while parsing dates")

dates = [ ts.strftime('%Y%m%d') for ts in dates_ts] 
print(dates)
logging.info(f"There are {len(dates)} dates in the given range. Start crawling!")


for date in dates:
	logging.info(f"Start crawling for date : {date}")
	try:
		start = time.time()

		result = dailyCrawl(date)
		# success write
		logging.info(f"crawl for date:{date} completed")
		with open(f'./tmp/{date}.pickle', 'wb') as f:
			pickle.dump(result, f)
		
		end = time.time()
		logging.info(f"write success in : {int(end-start)}(s)")
		
	except BaseException as e:
		logging.error(f"crawl failed or write fail for date: {date} - {e}")
		pass

logging.info("program terminated")

import pykrx

from pykrx import stock


def getTickerMapping():
	result = {}
	for ticker in stock.get_market_ticker_list():
		name = stock.get_market_ticker_name(ticker)
		result[ticker]=name
	return result

def getNameMapping():
	result = {}
	for ticker in stock.get_market_ticker_list():
		name = stock.get_market_ticker_name(ticker)
		result[name]=ticker
	return result

def isMarketOpen(date:str):
	#20xx-xx-xx
	date = date.replace('-', '')
	q = stock.get_previous_business_days(fromdate=date, todate=date)
	assert len(q) <= 1
	if len(q) == 0 or date[:4]=="2022":
		return False
	return True
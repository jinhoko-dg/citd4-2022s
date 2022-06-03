# TODO logic not finished yet

import yaml

from pykrx.pykrx import stock
from pykrx.pykrx.website.krx.krx_proxy import Proxy

# initialize proxy
with open('private.yaml') as f:
	private = yaml.load(f, Loader=yaml.FullLoader)
	token = private['PROXY_KEY']
assert token != ""

globalProxy = Proxy( firstInit = True, proxyDebug = True )
globalProxy.generate_proxy_list(token)
globalProxy.set_enable_proxy(True)

totalProxies = len(Proxy().proxy_list)
assert totalProxies != 0


invalidProxiesCnt = 0
date = "20211025"
for _ in range(totalProxies):
	try:
		df = stock.get_market_ohlcv_by_ticker(date, market="ALL")
	except:
		invalidProxiesCnt += 1

print(f"{ totalProxies } proxies in total")
print(f"{ invalidProxiesCnt } proxies are valid")
# import json
# import tqdm
# import yaml
# import pickle
# import sys
# import logging
# import random
# import time

# from ..pykrx.pykrx import stock
# from ..pykrx.pykrx.website.krx.krx_proxy import Proxy

# from concurrent.futures import ThreadPoolExecutor

# # initialize proxy
# with open('../private.yaml') as f:
# 	private = yaml.load(f, Loader=yaml.FullLoader)
# 	token = private['PROXY_KEY']
# assert token != ""

# globalProxy = Proxy( firstInit = True )
# globalProxy.generate_proxy_list(token)
# globalProxy.set_enable_proxy(True)

# test_proxy = globalProxy.get()
# print(f"test_proxy : {test_proxy}")


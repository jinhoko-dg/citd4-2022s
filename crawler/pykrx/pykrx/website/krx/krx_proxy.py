import requests
import yaml
import random

LINK_PREFIX = "https://proxy.webshare.io"
EMPTY_PROXY_DICT = { 'http': None, }


""" Singleton to store proxy """
class Proxy(object):
	def __new__(cls, *args, **kwargs):

		# Instantiaze for the first init 
		if not hasattr(cls, "instance"):
			cls.instance = super(Proxy, cls).__new__(cls)

		return cls.instance

	def __init__(ins, firstInit = False, proxyDebug = False):

		# bypass initialization when called from inner API
		if not firstInit:
			return

		ins.enable_proxy = False
		ins.proxy_token_updated = False
		ins.token = None
		ins.proxy_list = None
		ins.proxy_idx = None
		ins.current_proxy = None
		ins.proxyDebug = proxyDebug
		
		if 'value' not in ins.__dict__.keys():
			ins.value = EMPTY_PROXY_DICT

	def set_enable_proxy(ins, val:bool) :
		if val:
			ins.enable_proxy = True
		else:
			ins.enable_proxy = False

	def __getFullLink( ins, link: str) :
		return LINK_PREFIX + link
	
	def generate_proxy_list(ins, token: str):
		
		# check authentication
		response = requests.get( ins.__getFullLink("/api/profile/") , headers={"Authorization": token })
		assert response.status_code == 200
		
		ins.token = token
		
		# set proxy list
		pages = [1, 2]
		ins.proxy_list = []
		for page in pages:
			response = requests.get(ins.__getFullLink(f"/api/proxy/list/?page={str(page)}"), headers={"Authorization": ins.token })
			assert response.status_code == 200
				# TODO currently supports single page proxies
				# to support more, merge lists of all pages

			for item in response.json()['results']:
				ins.proxy_list.append( 
					{ "http" : f"http://{item['username']}:{item['password']}@{item['proxy_address']}:{item['ports']['http']}"  }
				)
		
		# shuffle
		random.shuffle( ins.proxy_list )
		print(f"Total proxies: {len(ins.proxy_list)}")

		# set index
		assert len(ins.proxy_list) > 0

		# TODO do not use index approach
		ins.proxy_idx = 0
		ins.proxy_token_updated = True


	def get(ins) -> dict :
		# TODO do not use index approach
		if not ins.enable_proxy:
			return EMPTY_PROXY_DICT

		assert ins.proxy_token_updated == True

		result = ( ins.proxy_list[ins.proxy_idx], ins.proxy_idx )

		ins.proxy_idx = 0 if ins.proxy_idx == len(ins.proxy_list) - 1 else ins.proxy_idx + 1

		# returns 
		return result[0]
	
	def invalidate_and_get(ins, invalid_proxy):
		pass
import requests
from abc import abstractmethod

DEBUG = False

class Get:
    def __init__(self):
        self.headers = { "User-Agent": "Mozilla/5.0" }
        self.proxies = { }
    def __init__(self, proxies:dict):
        self.headers = { "User-Agent": "Mozilla/5.0" }
        self.proxies = proxies

    def read(self, **params):
        if not self.headers:
            raise ValueError("Headers for read() is empty")
        if self.proxies:
            if DEBUG:
                print(f"Crawl using proxy : {self.proxies}\n")
            resp = requests.get(self.url, headers=self.headers, data=params, proxies=self.proxies)
        else:
            resp = requests.get(self.url, headers=self.headers, data=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        return NotImplementedError


class Post:
    def __init__(self):
        self.headers = { "User-Agent": "Mozilla/5.0" }
        self.proxies = {}

    def __init__(self, proxies:dict):
        self.headers = { "User-Agent": "Mozilla/5.0" }
        self.proxies = proxies

    def replaceProxy(self, proxies:dict):
        # only valid when proxy is already in-place
        assert len(self.proxies.keys()) is not 0
        self.proxies = proxies

    def read(self, **params):
        if not self.headers:
            raise ValueError("Headers for read() is empty")
        if self.proxies:
            if DEBUG:
                print(f"Crawl using proxy : {self.proxies}\n")
            resp = requests.post(self.url, headers=self.headers, data=params, proxies=self.proxies)
        else:
            resp = requests.post(self.url, headers=self.headers, data=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        return NotImplementedError



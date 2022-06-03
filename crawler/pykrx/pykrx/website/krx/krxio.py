from cmath import exp
import io
from abc import abstractmethod
from ...website.comm.webio import Post
from .krx_proxy import Proxy
import logging

DEBUG = True

class KrxWebIo(Post):
    def __init__(self):
        super().__init__( Proxy().get() )
        self.MAX_RETRIES = 10 # TODO set
        self.current_retry = 0

    def read(self, **params):
        params.update(bld=self.bld)
        resp = None
        try:
            resp = super().read(**params)
        except:
            if Proxy().proxyDebug:
                print(f"Proxy {self.proxies} fails")
                return

        # give a chance for retry
        isResultOk = False
        # logic 1 : if response code valid
        if resp != None and resp.status_code == 200:
            isResultOk = True
        # logic 2 : if response is convertable to json
        resp_json = None
        try:
            resp_json = resp.json()
        except:
            pass
        if resp_json is not None:
            isResultOk = True

        if not isResultOk:
            
            if self.current_retry >= self.MAX_RETRIES:
                if DEBUG:
                    print("RETRY LIMIT EXCEEDED!")
                raise Exception("Retry limit exceeded")

            # give it a try by re-registering proxy
            self.replaceProxy( Proxy().get() )
            self.current_retry += 1
            if DEBUG:
                print(f"retrying : {self.current_retry}")
            
            # recursively call read() again
            return self.read( **params )

        else:
            return resp_json      

    @property
    def url(self):
        return "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"

    @property
    @abstractmethod
    def bld(self):
        return NotImplementedError

    @bld.setter
    def bld(self, val):
        pass

    @property
    @abstractmethod
    def fetch(self, **params):
        return NotImplementedError


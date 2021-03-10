# -*- coding: utf-8 -*-
import random
import requests

from twisted.internet import defer
from twisted.internet.error import (
    ConnectError,
    ConnectionDone,
    ConnectionLost,
    ConnectionRefusedError,
    DNSLookupError,
    TCPTimedOutError,
    TimeoutError,
)
from twisted.web._newclient import ResponseNeverReceived
from twisted.web._newclient import ResponseFailed
from twisted.web.http import _DataLoss
from scrapy.core.downloader.handlers.http11 import TunnelError

class AuditDownloaderMiddleware(object):

    def __init__(self):
        
        self.EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseNeverReceived,
                           IOError, ResponseFailed, _DataLoss, TunnelError)
        self.ua = [
            'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:62.0) Gecko/20100101 Firefox/62.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:10.0) Gecko/20100101 Firefox/62.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
            'Chrome (AppleWebKit/537.1; Chrome50.0; Windows NT 6.3) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36']
            
        self.proxy_api = ''
        self.proxy_list = []

    def get_proxy_list(self):
        while len(self.proxy_list) == 0:
            try:
                r = requests.get(self.proxy_api)
                self.proxy_list = ['http://{}:{}'.format(x['IP'], x['Port']) for x in r.json()['data']]
            except:
                continue

    # def test_proxy(self, proxy):
    #     proxy = {'http': proxy}
    #     test_url = 'http://httpbin.org/ip'
    #     try:
    #         r = requests.get(test_url, proxies=proxy, timeout=1)
    #         if r.ok: return 1
    #         return 0
    #     except:
    #         return 0

    def remove_proxy(self, proxy):
        if proxy in self.proxy_list:
            self.proxy_list.remove(proxy)

    def change_proxy(self, request):
        self.get_proxy_list()
        proxy = random.choice(self.proxy_list)
        # while self.test_proxy(proxy) == 0:
        #     self.remove_proxy(proxy)
        #     self.get_proxy_list()
        #     proxy = random.choice(self.proxy_list)
        request.meta['proxy'] = proxy
        request.meta['download_timeout'] = 5
        return request    

    def process_request(self, request, spider):
        request = self.change_proxy(request)
        request.headers['user-agent'] = random.choice(self.ua)

    def process_response(self, request, response, spider):
        if response.status in [500, 502, 503, 504, 522, 524, 408, 429, 403]:
            self.remove_proxy(request.meta['proxy'])
            request = self.change_proxy(request)
            request.dont_filter = True
            return request
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            self.remove_proxy(request.meta['proxy'])
            request = self.change_proxy(request)
            request.dont_filter = True
            return request

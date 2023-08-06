import json
import re

import requests as rq

from . import (
    resources,
    utils
)

class StockxClient:
    BASE_URL = 'https://stockx.com'
    def __init__(self, fetch_context=False, custom_headers={}, proxies={}):
        
        self._session = rq.Session()
        self._session.headers.update({
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        })
        self._session.headers.update(custom_headers)
        self._session.proxies = proxies

        if fetch_context:
            self._context_values = self._fetch_context_values()

        self._resources = {
            'browse': resources.BrowsePool(
                utils.urljoin(self.BASE_URL, 'api/browse'), self._session
            ),
            'gql': resources.GQLPool(
                utils.urljoin(self.BASE_URL, '/api/p/e'), self._session
            ),
            'products': resources.ProductsPool(
                utils.urljoin(self.BASE_URL, '/api/products'), self._session
            )
        }

    def _fetch_context_values(self):
        index_res = self._session.get(self.BASE_URL)
        if index_res.status_code != 200:
            print('Error {} loading context values'.format(index_res.status_code))
            return

        expressions = {
            'session_id': ['window.sessionId = \'"(.+?)"\';', lambda value: value],
            'app_config': ['window.appConfig = (.+?);', json.loads],
            'app_id': ['window._pxAppId = \'(.+?)\';', lambda value: value]
        }

        context_values = {
            k: caster(re.findall(expression, index_res.text)[0])
            for k, (expression, caster) in expressions.items()
        }
        context_values.update({
            'auth_client_id': 'eyJuYW1lIjoiYXV0aDAuanMiLCJ2ZXJzaW9uIjoiOS4xOS4wIn0='
        })

        return context_values

    @property
    def resources(self):
        return self._resources

    @property
    def browse(self):
        return self._resources['browse']

    @property
    def gql(self):
        return self._resources['gql']

    @property
    def products(self):
        return self._resources['products']        

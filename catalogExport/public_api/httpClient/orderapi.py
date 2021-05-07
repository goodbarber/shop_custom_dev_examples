import requests

from urllib.parse import urljoin, urlencode

from public_api import config
from public_api.httpClient.callapi import CallApi


class OrderApi(CallApi):
    '''Class that call public API order endpoint'''
    def __init__(self):
        self.url = urljoin(config.PUBLIC_API_DOMAIN,
                           f"orders/{config.WEBZINE_ID}/")
        self.headers = {
            'token': config.ACCESS_TOKEN
        }

    def list_all_orders(self):
        return self.get(self.url, self.headers)

    def list_all_orders_by_status(self, status, page=1):
        query = f'?{urlencode(dict(status=status, page=page))}'
        return self.get(urljoin(self.url, query), self.headers)

    def retrieve_an_order(self, order):
        return self.get(urljoin(self.url, order.id), self.headers)

    def get_status_of_an_order(self, order):
        order_id = order.id
        return self.get(urljoin(self.url,
                                f'order/{order_id}/shipping/'),
                        self.headers)

    def update_status_order(self, order, data):
        order_id = order.id
        return self.patch(urljoin(self.url, f'order/{order_id}/shipping/'),
                          data,
                          self.headers)

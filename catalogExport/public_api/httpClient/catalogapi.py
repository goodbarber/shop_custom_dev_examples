import requests

from urllib.parse import urljoin, urlencode

from public_api.httpClient.callapi import CallApi
from public_api import config


class CatalogApi(CallApi):
    '''Class that call public API catalog endpoint'''
    def __init__(self):
        self.url = urljoin(
            config.PUBLIC_API_DOMAIN,
            f"catalog/{config.WEBZINE_ID}/")

        self.headers = {
            'token': config.ACCESS_TOKEN
        }

    def retrieve_product_variant_details(self, product, variant):
        product_id = product.get('id')
        variant_id = variant.get('id')
        return self.get(urljoin(self.url,
                        f'product/{product_id}/variant/{variant_id}'),
                        self.headers)

    def list_all_products(self, page=1):
        query = f'?{urlencode(dict(page=page))}'
        return self.get(urljoin(self.url, urljoin('products', query)),
                        self.headers)

    def update_variant_stock(self, product, variant, data):
        product_id = product.get('id')
        variant_id = variant.get('id')
        return self.patch(urljoin(self.url,
                          f'product/{product_id}/variant/{variant_id}/'),
                          data,
                          self.headers)

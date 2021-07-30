import requests

from urllib.parse import urljoin, urlencode

from .callapi import CallApi
from .. import config


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

    def retrieve_product_details(self, product):
        product_id = product.get('id')
        return self.get(urljoin(self.url,
                        f'product/{product_id}/'),
                        self.headers)

    def list_all_products(self, page=1):
        query = f'?{urlencode(dict(page=page))}'
        return self.get(urljoin(self.url, urljoin('product/', query)),
                        self.headers)

    def update_variant_stock(self, product, variant, data):
        product_id = product.get('id')
        variant_id = variant.get('id')
        return self.patch(urljoin(self.url,
                          f'product/{product_id}/variant/{variant_id}/'),
                          data,
                          self.headers)

    def create_a_product(self, data):
        # print(urljoin(self.url, 'product/'))
        return self.post(urljoin(self.url, 'product/'),
                         data=data,
                         headers=self.headers)

    def create_a_variant(self, product_id, data):
        # print(urljoin(self.url,
        #               f'product/{product_id}/variant/'))
        return self.post(urljoin(self.url,f'product/{product_id}/variant/'),
                         data=data,
                         headers=self.headers)

    def upload_a_product_slide(self, product_id, data):
        print(urljoin(self.url,
                      f'product/{product_id}/slide/'))
        return self.upload_file(urljoin(self.url,f'product/{product_id}/slide/'),
                         data=data,
                         headers=self.headers)

    def list_all_collections(self):
        return self.get(urljoin(self.url, 'collection'),
                        headers=self.headers)

    def list_all_options(self):
        return self.get(urljoin(self.url, 'option/'),
                        headers=self.headers)

    def update_product(self, product_id, data):
        return self.patch(urljoin(self.url, f'product/{product_id}/'),
                          data=data,
                          headers=self.headers)

    def delete_a_product_slide(self, product_id, slide_id):
        return self.delete(urljoin(self.url, f'product/{product_id}/slide/{slide_id}/'),
                          headers=self.headers)

    def delete_a_product(self, product_id):
        return self.delete(urljoin(self.url, f'product/{product_id}/'),
                          headers=self.headers)

    def upload_a_product_pdf(self, product_id, data):
        return self.upload_file(urljoin(self.url, f'product/{product_id}/pdf/'),
                         data=data,
                         headers=self.headers)

    def delete_a_product_pdf(self, product_id):
        return self.delete(urljoin(self.url, f'product/{product_id}/pdf/'),
                         headers=self.headers)

    def create_a_variant_option(self, data):
        try:
            res = self.post(urljoin(self.url, 'option/'),
                         data=data,
                         headers=self.headers)
            return res
        except requests.exceptions.HTTPError as err:
            return res

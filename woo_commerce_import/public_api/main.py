import requests
import json

from .src.httpClient.catalogapi import CatalogApi
from .src.httpClient.orderapi import OrderApi

class TestPublicApi(object):
    catalog_api = CatalogApi()
    order_api = OrderApi()

    def get_products(self):
        ''' TEST GET PRODUCTS '''
        all_products = self.catalog_api.list_all_products()
        print(all_products)

    def get_orders(self):
        ''' TEST GET ORDERS '''
        all_orders = self.order_api.list_all_orders()
        print(all_orders)

    def create_product(self):
        ''' TEST CREATE PRODUCT '''
        data = {
            'title': 'tomate',
            'summary': 'Une tomate',
            'status': 'PUBLISHED',
            'slug': 'tomate',
            'tags': ['légumes'],
            'collections': [639471],
            'set_custom_similar_products': [],
            'product_ref': 'TOM'
        }
        res = self.catalog_api.create_a_product(data)
        print(res.json())

    def create_variant(self):
        ''' TEST CREATE VARIANT '''
        data = {
            'stock': 10,
            'sku': 'TOM',
            'price': '3.30',
            'option_values': []
        }
        res = self.catalog_api.create_a_variant(4595653, data)
        print(res.json())

    def upload_slide(self):
        ''' TEST UPLOAD IMAGE '''
        url_image = 'https://upload.wikimedia.org/wikipedia/commons/d/db/Patern_test.jpg'
        data = {}
        res = requests.get(url_image)
        try:
            data['image_file'] = ('test.png', res.content, 'image/png')
            res = self.catalog_api.upload_a_product_slide(4595653, data)
            print(res.json())
        except Exception as e:
            print(e)

    def get_collections(self):
        ''' TEST GET COLLECTIONS '''
        res = self.catalog_api.list_all_collections()
        print(res.json())

    def get_options(self):
        ''' TEST GET OPTIONS VARIANT '''
        res = self.catalog_api.list_all_options()
        print(res.json())

    def create_option(self):
        option = {
            "name": "colors"
        }
        res = self.catalog_api.create_a_variant_option(option)
        print(res)


def main():
    test_public_api = TestPublicApi()
    # test_public_api.get_collections()
    # test_public_api.create_product()
    # test_public_api.create_variant()
    # test_public_api.upload_slide()
    # test_public_api.get_options()
    test_public_api.create_option()

if __name__ == '__main__':
    main()
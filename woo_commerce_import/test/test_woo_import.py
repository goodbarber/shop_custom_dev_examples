import json
import unittest

from unittest import mock

from woo_commerce.import_process import WooImportProcess, GbOption
from woo_commerce.import_process import UtilTreatment
from public_api.src.httpClient.catalogapi import CatalogApi

class TestWooImport(unittest.TestCase):
    PATH_TEST = "test/data"
    def setUp(self):
        self.patcher = mock.patch('public_api.src.httpClient.catalogapi.CatalogApi.list_all_collections')
        self.mock_foo = self.patcher.start()
        self.patcher = mock.patch('public_api.src.httpClient.catalogapi.CatalogApi.list_all_options')
        self.mock_foo = self.patcher.start()
        self.woo_import_process = WooImportProcess()
        with open(f"{self.PATH_TEST}/woo_commerce.json", "r") as woo_file:
            self.data_woo_commerce = json.load(woo_file)
        with open(f"{self.PATH_TEST}/goodbarber.json", "r") as gb_file:
            self.data_goodbarber = json.load(gb_file)
        with open(f"{self.PATH_TEST}/woo_variant.json", "r") as w_variant_file:
            self.woo_variant = json.load(w_variant_file)

    @mock.patch.object(WooImportProcess, 'get_existing_collections', return_value=[778836])
    def test_parse_product(self, mock_collections):
        """
        Test parsing of woo commerce product to GoodBarber Format
        """
        woo_product = self.data_woo_commerce[0]
        parse_product = self.woo_import_process.parse_detail_product(woo_product)
        gb_product = {
            'title': "Hoodie",
            'summary': "The GoodBarber Hoodie\n",
            'status': "PUBLISHED",
            'slug': "hoodie",
            'tags': [],
            'collections': [778836],
            'set_custom_similar_products': [],
            'product_ref': 14,
        }
        self.assertDictEqual(parse_product, gb_product)

    def test_parse_options(self):
        woo_product = self.data_woo_commerce[3]
        parse_options = self.woo_import_process.parse_options(woo_product)
        parse_option1 = parse_options[0]
        gb_option1 = GbOption(name="Taille", id_gb="")
        self.assertEqual(gb_option1, parse_option1)

    @mock.patch("public_api.src.httpClient.catalogapi.requests.post")
    def test_create_options(self, mock_create_option):
        mock_create_option.return_value.status_code = 200
        mock_create_option.return_value.json.return_value = {
            'id': 15
        }
        woo_product = self.data_woo_commerce[3]
        parse_options = self.woo_import_process.parse_options(woo_product)
        self.woo_import_process.create_options_in_gb(parse_options)
        all_parse_options = [GbOption(name="Taille", id_gb="15")]
        self.assertListEqual(all_parse_options, self.woo_import_process.gb_parse_options)
        # ERROR 400
        self.woo_import_process.gb_parse_options = []
        mock_create_option.return_value.status_code = 400
        mock_create_option.return_value.json.return_value = {
            'Error': "error"
        }
        self.woo_import_process.create_options_in_gb(parse_options)
        self.assertNotEqual(all_parse_options, self.woo_import_process.gb_parse_options)

    def test_recover_gb_option(self):
        attributes_variant = self.woo_variant.get('attributes')[0]
        gb_option = self.woo_import_process.recover_gb_option(attributes_variant)
        test_option = GbOption(name="Taille", id_gb="15")
        self.assertEqual(gb_option, test_option)

    def test_parse_options_values(self):
        parse_options_values = self.woo_import_process.parse_options_values(self.woo_variant)
        gb_format = [
                {
                    "15": "S"
                }
            ]
        self.assertListEqual(parse_options_values, gb_format)

    @mock.patch("woocommerce.API.get")
    def test_parse_variant(self, mock_wcapi):
        """
        Test parsing of woo commerce variants to GoodBarber Format
        """
        mock_wcapi.return_value.status_code = 200
        mock_wcapi.return_value.json.return_value = self.woo_variant
        #PARSING NO VARIANT OPTIONS
        woo_product = self.data_woo_commerce[0]
        gb_api_product = self.data_goodbarber[0]
        parse_variant = self.woo_import_process.parse_detail_variant(woo_product, gb_api_product)
        gb_variant = {
            'price': "50.00",
            'sku': woo_product.get('sku'),
            'option_values': [],
            'stock': woo_product.get('stock_quantity') if woo_product.get('stock_quantity') else 0,
            'weight': self.woo_import_process.util.convert_grams_in_kilo(int(woo_product.get('weight'))) if woo_product.get('weight') != '' else 0
        }
        self.assertDictEqual(parse_variant[0], gb_variant)
        #PARSING WITH VARIANTS OPTIONS
        woo_product = self.data_woo_commerce[3]
        parse_variant = self.woo_import_process.parse_detail_variant(woo_product, gb_api_product)
        gb_variant = {
            'price': "20.00",
            'sku': self.woo_variant.get('sku'),
            'option_values': [
                {
                    "15": "S"
                }
                ],
            'stock': self.woo_variant.get('stock_quantity') if self.woo_variant.get('stock_quantity') else 0,
            'weight': self.woo_import_process.util.convert_grams_in_kilo(int(self.woo_variant.get('weight'))) if self.woo_variant.get('weight') != '' else 0
        }
        self.assertDictEqual(gb_variant, parse_variant[0])


class TestUtilTreatmen(unittest.TestCase):
    def setUp(self):
        self.util = UtilTreatment()

    def test_clean_html(self):
        """
        Test of strip the html tags method of util treatment class
        """
        raw_html = "<p>The GoodBarber famous T-Shirt</p>\n"
        clean_html = self.util.cleanhtml(raw_html)
        result_compare = "The GoodBarber famous T-Shirt\n"
        self.assertEqual(clean_html, result_compare)

if __name__ == '__main__':
    unittest.main()
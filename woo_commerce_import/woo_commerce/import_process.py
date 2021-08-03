import logging
import re
import requests

from woo_commerce import config

from woocommerce import API
from public_api.src.httpClient.catalogapi import CatalogApi


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


class Collection(object):
    """
    Class to represent a collection in order to compare both woo and gb
    with the equals method
    """
    def __init__(self, **kwargs):
        self.id: int = kwargs.get('id')
        self.name: str = kwargs.get('name')

    def __eq__(self, obj):
        return self.name == obj.name


class GbOption(object):
    """
    Class to represent a variant option of goodbarber
    product, in order to compare it
    """
    def __init__(self, name: str, id_gb: str=""):
        self.id = id_gb
        self.name = name.lower()

    def __eq__(self, obj):
        return self.name == obj.name

    def __str__(self):
        return self.name


class Picture(object):
    """
    Class to represent a picture in order to compare both woo and gb
    with the equals method
    """
    def __init__(self, **kwargs):
        self.url_woo = kwargs.get('src')
        self.name = kwargs.get('name')
        self.extension = kwargs.get('extension')
        self.id_pict_gb = kwargs.get('id_pict_gb')

    def __eq__(self, obj):
        return self.name == obj.name

    def __str__(self):
        return self.name


class UtilTreatment(object):
    """
    Allow to do specific treatment on data
    """
    VAT_RATE = 10

    def apply_vat_rate(self, price: float):
        return (price) + round(price / 100 * self.VAT_RATE, 2)

    def convert_grams_in_kilo(self, weight):
        return weight / 1000

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext


class WooImportProcess(object):
    """
    Class that specify all the process needed for the catalog
    import from woo commerce platform
    """
    catalog_public_api = CatalogApi()
    gb_parse_options = []
    util = UtilTreatment()
    wc_api = API(
        url=config.URL_WOO,
        consumer_key=config.CONSUMER_KEY,
        consumer_secret=config.CONSUMER_SECRET,
        version="wc/v3"
        )

    def __init__(self, product_per_page=100, status="all",
                 variant=True, picture=True):
        gb_collections = self.catalog_public_api.list_all_collections().json()
        self.collections_shop = [Collection(**collection)
                                 for collection in gb_collections.get('collections')]
        self.product_per_page = product_per_page
        self.status = status
        self.variant = variant
        self.picture = picture
        self.all_options = self.catalog_public_api.list_all_options().json()

    def init_catalog_gb(self):
        """
        Import the woo commerce catalog to GoodBarber shop
        """
        woo_catalog = self.get_woo_commerce_catalog()
        self.parse_woo_commerce_catalog(woo_catalog)

    def get_woo_commerce_catalog(self):
        """
        Get the woo commerce catalog
        """
        data = []
        next_page = True
        page = 1
        while next_page:
            res = self.wc_api.get('products', params={
                "per_page": self.product_per_page,
                "page": page
                })
            urls = res.headers["link"].split(',')
            urls = {url.split(";")[1].strip():url.split(";")[0].strip() for url in urls}
            next_page = urls.get('rel="next"') != None and self.product_per_page == 100
            page += 1
            data += res.json()
        return data

    def return_right_status_condition(self, woo_product):
        if self.status == "all":
            return (woo_product.get('status') == "publish" 
                    or woo_product.get('status') == "private")
        else:
            return woo_product.get('status') == self.status

    def parse_detail_product(self, woo_product):
        """
        Method that allow to parse the detail products in GoodBarber format
        """
        woo_categories = [Collection(**category) for category in woo_product.get('categories')]
        collections_ids = self.get_existing_collections(woo_categories)
        if len(collections_ids) == 0:
            logging.info('No collection corresponding')
        gb_product = {
            'title': woo_product.get('name'),
            'summary': self.util.cleanhtml(woo_product.get('description')),
            'status': self.get_status_product_correspondence(woo_product.get('status')),
            'slug': woo_product.get('slug'),
            'tags': [tag.get('name') for tag in woo_product.get('tags')],
            'collections': collections_ids,
            'set_custom_similar_products': [],
            'product_ref': woo_product.get('id'),
        }
        logging.info(f"GB product with slug {gb_product.get('slug')}"
                     "will be created in public api")
        return gb_product

    def parse_options(self, woo_product):
        """
        Parse woo commerce attributes and return an array of
        goodbarber options
        """
        all_options = []
        for attribute in woo_product.get('attributes'):
            gb_attribute_object = GbOption(name=attribute.get('name'), id_gb="") 
            all_options.append(gb_attribute_object)
        return all_options

    def create_options_in_gb(self, options):
        """
        Method that allow to create options in GoodBarber app.
        All the options referenced in the variant will be created.
        If already created, the options will be recover by the public api.
        """
        for option in options:
            option_data = {
                "name": option.name
            }
            res = self.catalog_public_api.create_a_variant_option(option_data)
            if res.status_code >= 200 and res.status_code < 300:
                gb_data = res.json()
                option.id = str(gb_data.get('id'))
                self.gb_parse_options.append(option)
            elif res.status_code >= 400:
                logging.info("ERROR CREATING OPTION VARIANT, GET THE OPTIONS")
                for option in self.all_options.get('options'):
                    if option.get('name') == option_data.get('name'):
                        self.gb_parse_options.append(GbOption(name=option.get('name'),
                                                              id_gb=option.get('id')))
                        logging.info(f"Get the option with name "
                                     f"{option.get('name')} already created")
                        break

    def recover_gb_option(self, woo_attribute):
        """
        Recover the gb option associated with the woo commerce variant
        option attribute
        """
        gb_option_woo = GbOption(name=woo_attribute.get('name'))
        for gb_option in self.gb_parse_options:
            if gb_option == gb_option_woo:
                return gb_option
        return None

    def parse_options_values(self, woo_variant):
        """
        Parse the option values from the woo variant into
        a goodbarber format
        """
        all_options_data = []
        for attribute in woo_variant.get("attributes"):
            gb_option = self.recover_gb_option(attribute)
            gb_option_data = {
                f"{gb_option.id}": attribute.get("option")
            }
            all_options_data.append(gb_option_data)
        print("ALL OPTIONS DATA: ", all_options_data)
        return all_options_data

    def parse_detail_variant(self, woo_product, product_gb_api):
        """
        Parse the detail variant coming from woo commerce into
        GoodBarber format
        """
        id_product = product_gb_api.get('id')
        woo_price = float(format(float(woo_product.get('price')), '.2f'))
        # if woo_product.get('price') != "":
        #     woo_price = self.util.apply_vat_rate(woo_price)
        woo_price = format(woo_price, '.2f')
        logging.info(f"ID product from gb: {id_product}")
        woo_variations = woo_product.get('variations')
        all_variants = []
        if len(woo_variations) > 0 and self.variant:
            parse_opt = self.parse_options(woo_product)
            self.create_options_in_gb(parse_opt)
            for id_variant in woo_variations:
                woo_variant = self.wc_api.get(f"products/"
                                              f"{id_product}/variations/{id_variant}").json()
                woo_price = float(format(float(woo_variant.get('price')), '.2f'))
                woo_price = format(woo_price, '.2f')
                gb_variant = {
                    'price': woo_price if woo_variant.get('price') != "" else "0.00",
                    'sku': woo_variant.get('sku'),
                    'option_values': self.parse_options_values(woo_variant),
                    'stock': woo_variant.get('stock_quantity')
                    if woo_variant.get('stock_quantity') else 0,
                    'weight': self.util.convert_grams_in_kilo(
                        int(woo_variant.get('weight')))
                    if woo_variant.get('weight') != '' else 0
                }
                logging.info(f'gb_variant with sku {gb_variant.get("sku")}')
                if woo_variant.get('price') != woo_variant.get('regular_price'):
                    gb_variant['compare_at'] = woo_variant.get('regular_price')
                all_variants.append(gb_variant)
        else:
            gb_variant = {
                'price': woo_price if woo_product.get('price') != ""
                else "0.00",
                'sku': woo_product.get('sku'),
                'option_values': [],
                'stock': woo_product.get('stock_quantity')
                if woo_product.get('stock_quantity') else 0,
                'weight': self.util.convert_grams_in_kilo(
                    int(woo_product.get('weight')))
                if woo_product.get('weight') != '' else 0
            }
            logging.info(f'gb_variant with sku {gb_variant.get("sku")}')
            if woo_product.get('price') != woo_product.get('regular_price'):
                gb_variant['compare_at'] = woo_product.get('regular_price')
            all_variants.append(gb_variant)
        return all_variants

    def get_existing_collections(self, woo_commerce_product_categories):
        """
        Get the existing ids of collections if exist in GB
        """
        ids_collections = []
        for category in self.collections_shop:
            if category in woo_commerce_product_categories:
                ids_collections.append(category.id)
        return ids_collections

    def parse_woo_commerce_catalog(self, woo_commerce_catalog):
        """
        Parse the woo commerce product to GB Format and create all
        the products
        """
        for product in woo_commerce_catalog:
            # Create collection if doesn't exist into back office
            if self.return_right_status_condition(product):
                created = self.parse_woo_product_and_create(product)
                if not created:
                    continue

    def parse_woo_product_and_create(self, product):
        """
        Parse the woo product and trigger the process to create entirely
        the product in GB Shop
        """
        gb_product = self.parse_detail_product(product)
        product_gb_api = self.catalog_public_api.create_a_product(gb_product).json()
        # Upload all images
        if len(product.get('images')) > 0 and self.picture:
            for image_object in product.get('images'):
                self.upload_image_product(image_object, product_gb_api)
        gb_variants = self.parse_detail_variant(product, product_gb_api)
        id_gb_product = product_gb_api.get('id')
        for gb_variant in gb_variants:
            id_variant = self.catalog_public_api.create_a_variant(
                id_gb_product,
                gb_variant).json().get('id')
            logging.info(f'VARIANT Created in GB: {id_variant}')
        return True

    def upload_image_product(self, woo_image_object, product_gb):
        """
        Get the product's image with the url and upload it with public API
        """
        data = {}
        extension = woo_image_object.get("src").split('/')[-1].split('.')[-1]
        logging.info(f"src image {woo_image_object.get('src')}")
        image_rsrc = requests.get(woo_image_object.get('src'))
        try:
            name_img = f"{woo_image_object.get('name')}.{extension}"
            data['image_file'] = (name_img, image_rsrc.content,
                                  self.get_right_filetype(extension))
            res = self.catalog_public_api.upload_a_product_slide(
                product_gb.get('id'), data).json()
            logging.info(f"Upload image {res}")
            if not product_gb.get('media'):
                thumbnail = {"media": res.get('id')}
                res_thumbnail = self.catalog_public_api.update_product(
                    product_gb.get('id'),
                    thumbnail)
                logging.info(f"Update Thumbnail {res_thumbnail}")
        except Exception as e:
            logging.error(e)

    def create_gb_product(self, product):
        """
        Create the gb product
        """
        res = self.catalog_public_api.create_a_product(product).json()
        # print("Response create product: ", res.json())
        return res

    def get_status_product_correspondence(self, status_woo_commerce):
        """
        Get the GB product status correspondence
        """
        status_correspondence = {
            'publish': 'PUBLISHED',
            'draft': 'DRAFT',
            'private': 'INVISIBLE',
            'pending': 'DRAFT'
        }
        return status_correspondence[status_woo_commerce]

    def update_pb_api_stock(self, id_product, id_variant, new_stock):
        """
        Update the goodbarber stock with the public API
        """
        res = self.catalog_public_api.update_variant_stock(
            {
                'id': id_product
            },
            {
                'id': id_variant
            },
            {
                'stock': new_stock
            }
        )
        logging.info(f"Response Update GB Product: {res}")

    def get_right_filetype(self, extension):
        """
        Get the good filetype to upload picture
        """
        correspondence = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'jpx': 'image/jpx',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'cr2': 'image/x-canon-cr2',
            'tif': 'image/tiff',
            'bmp': 'image/bmp',
            'jxr': 'image/vnd.ms-photo',
            'psd': 'image/vnd.adobe.photoshop',
            'ico': 'image/x-icon',
            'heic': 'image/heic'
        }
        file_type = correspondence.get(extension)
        logging.info(f"file_type: {file_type}")
        return file_type if not None else "image/png"

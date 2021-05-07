import logging

from urllib.parse import urljoin, urlparse, urlencode

from model.mode import Mode
from public_api import config as idgb
from public_api.httpClient.catalogapi import CatalogApi
from public_api.httpClient.catalogapi import CatalogApi
from public_api.model.product import Product


class GBCatalogExport(object):

    def __init__(self):
        self.catalog_api = CatalogApi()

    def get_next_page(self, res):
        """Get the next page of the catalog

        Args:
            res (HttpResponse): The response from the Public API

        Returns:
            (int): The next page for the catalog
        """
        next_page = res['next']
        logging.info(f"Next page: {next_page}")
        if next_page is not None:
            u = urlparse(next_page)
            query_tab = u.query.split('&')
            query_dict = {q.split('=')[0]: q.split('=')[1] for q in query_tab}
            return query_dict['page']
        return None

    def get_catalog(self, page=1):
        """Get the GB catalog

        Args:
            page (int, optional): Catalog page Defaults to 1.

        Returns:
            HttpResponse: Response from the public API
        """
        res = self.catalog_api.list_all_products(page=page)
        return res.json()

    def format_catalog(self, mode: int, page: int = 1, collection: str = None):
        """Format the catalog

        Args:
            mode (int): GOOGLE=1, FB=2, ALL=3
            page (int): Catalog page
            collection (str): Collection filter of products default None

        Returns:
            (array): array formated for Mode
        """
        res = self.get_catalog(page)
        products = [Product(**product) for product in res['products']]
        if collection:
            products = filter(lambda p: any(c.name == collection for c in p.collections), products)

        working_arr = []
        for product in products:
            for variant in product.variants:
                if not variant.sku or variant.sku == "--":
                    logging.error(f"""Product #{product.id}-{variant.id} """
                                f"""({product.title}) has no SKU, discarding""")
                    continue

                if not product.summary:
                    logging.error(f"""Product #{product.id}-{variant.id} """
                                  f"""({product.title}) has no description, discarding""")
                    continue

                # Create new dict in the product array to store the current variant
                work_dict = {}

                try:
                    # Google wants the sku to be a separate field
                    work_dict["id"] = variant.sku if variant.sku != '--' else variant.id
                    work_dict["item_group_id"] = product.id

                    # Global fields
                    work_dict["title"] = product.title
                    work_dict["description"] = product.summary
                    work_dict["price"] = "{0:.2f} {1}".format(float(variant.price), idgb.CURRENCY)
                    work_dict["mpn"] = variant.sku
                    work_dict["availability"] = "in stock" if variant.stock != 0 else "out of stock"
                    work_dict["condition"] = "new"
                    work_dict["link"] = f"{idgb.SHOP_URL}/products/{product.slug}"
                    work_dict["image_link"] = product.media["thumbnails"]["square"]["large"]
                    work_dict["brand"] = idgb.APP_NAME
                    work_dict["google_product_category"] = None
                    working_arr.append(work_dict)

                except Exception as e:
                    print(e)

        return working_arr + \
                             (self.format_catalog(mode=mode,
                                                  page=self.get_next_page(res),
                                                  collection=collection)
                              if (self.get_next_page(res) is not None) else [])

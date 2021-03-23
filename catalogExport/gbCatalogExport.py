import argparse
import csv
import logging
import requests
import sys
from urllib.parse import urljoin

from config import Config, Mode

out_filename = "export"

class localConfig:
	API_BASE_URL = "https://commerce.goodbarber.dev"


def formatCatalog(endpoint: str, token: str, mode: int):
    """Retrieves a GB catalog and formats it to use with third party shopping platforms

    Args:
        endpoint (str): GB Api endpoint
        token (str): GB API Token
        mode (int): 0=FB, 1=Google

    Raises:
        HTTPError: The GB API called has failed
    """

    req = requests.get(urljoin(localConfig.API_BASE_URL, endpoint),
                       headers={"token": token})

    logging.debug("Sent /catalog req")

    if req.status_code == 200:
        req = req.json()
    else:
        raise requests.models.HTTPError(
            f"HTTP {req.status_code}, aborting.\nBody: {req.text}")

    working_arr = []

    for product in req["products"]:

        for variant in product["variants"]:

            if not variant["sku"] or variant["sku"] == "--":
                logging.error(f"""Product #{product['id']}-{variant['id']} """
                              f"""({product['title']}) has no SKU, discarding""")
                continue

            if not product["summary"]:
                logging.error(f"""Product #{product['id']}-{variant['id']} """
                              f"""({product['title']}) has no description, discarding""")
                continue

            # Create a new dict in the product array to store the current variant
            work_dict = {}

            try:
                # Google wants the SKU to be a separate field
                work_dict["id"] = product["id"] if mode == 1 else variant["sku"]

                if mode == Mode.GOOGLE:
                    # Google Shopping specific field
                    # The ID is set with the product ID by default
                    # If the SKU is set, we fill it with the SKU
                    work_dict["item_group_id"] = variant["id"]

                # Global fields
                work_dict["title"] = product["title"]
                work_dict["description"] = product["summary"]
                work_dict["price"] = variant["price"]
                work_dict["mpn"] = variant["sku"]
                work_dict["availability"] = "in stock" if variant["stock"] != 0 else "out of stock"
                work_dict["condition"] = "new"
                work_dict["link"] = f"{Config.SHOP_URL}/products/{product['slug']}"
                work_dict["image_link"] = product["media"]["thumbnails"]["square"]["large"]

                # Global but unavailable at this point
                # ? We can use the MPN for FB, but not for Google
                work_dict["brand"] = None
                work_dict["google_product_category"] = None

                """
                #Clothing
                working_dict["age"]=None
                working_dict["color"]=None
                working_dict["gender"]=None
                working_dict["size"]=None

                working_dict["vat"]=None #! Mandatory for US based shops
                """

                working_arr.append(work_dict)

            except Exception as e:
                print(e)

    return working_arr + formatCatalog(req["next"], token, mode) if req["next"] else []


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--file", type=str, 
                            help="Chose the csv file that will be write")
        arg_file = parser.parse_args()
        if not arg_file.file:
            raise argparse.ArgumentError(arg_file, "Please inform the csv that will be write with option -f")
        out_filename = arg_file.file
    except argparse.ArgumentError as e:
        logging.error(e)
        sys.exit(1)

    productsFinal = formatCatalog(f"/publicapi/v1/general/catalog/{Config.WEBZINE_ID}/products",
                                  Config.GB_TOKEN,
                                  Config.MODE)

    with open(f"{out_filename}.csv", 'w', newline='') as of:
        dw = csv.DictWriter(of, productsFinal[0].keys())
        dw.writeheader()
        dw.writerows(productsFinal)

    logging.info("Export done")

import argparse
import csv
import logging
import sys

from urllib.parse import urljoin, urlparse, urlencode

from model.mode import Mode
from model.gb_catalog_export import GBCatalogExport
from public_api.httpClient.catalogapi import CatalogApi


out_filename = "export"


def main():
    logging.basicConfig(level=logging.INFO)

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--file", type=str,
                            help="Inform the tsv filename that will be write")
        arg_file = parser.parse_args()
        if not arg_file.file:
            raise argparse.ArgumentError(arg_file, ("Please inform the tsv filename that will"
                                                    " be write with option -f"))
        out_filename = arg_file.file
    except argparse.ArgumentError as e:
        logging.error(e)
        sys.exit(1)

    try:
        gb_catalog_export = GBCatalogExport()
        productsFinal = gb_catalog_export.format_catalog(Mode.ALL)

        with open(f"{out_filename}.tsv", 'w', newline='') as of:
            dw = csv.DictWriter(of, productsFinal[0].keys(), delimiter='\t')
            dw.writeheader()
            dw.writerows(productsFinal)

        logging.info("Export done")
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()

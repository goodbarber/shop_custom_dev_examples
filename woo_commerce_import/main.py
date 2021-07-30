from public_api import main
from woo_commerce.import_process import WooImportProcess


def run_import():
    import_process = WooImportProcess(product_per_page=100)
    import_process.init_catalog_gb()


if __name__ == '__main__':
    run_import()

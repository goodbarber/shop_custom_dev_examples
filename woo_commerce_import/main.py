from public_api import main
from management.commands.command import ImportCommand
from woo_commerce.import_process import WooImportProcess


def run_import():
    args_command = ImportCommand().args
    import_process = WooImportProcess(product_per_page=args_command.perpage,
                                      status=args_command.status,
                                      variant=args_command.variant,
                                      picture=args_command.image)
    import_process.init_catalog_gb()


if __name__ == '__main__':
    run_import()

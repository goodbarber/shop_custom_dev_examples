import argparse


class ImportCommand(object):
    """
    Custom command handler that allow to create the
    woo commerce import
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.args = None
        self.define()

    def define(self):
        """
        Define all the arguments in the argument parser
        """
        self.parser.add_argument(
            "-p",
            "--perpage",
            type=int,
            help="Define a number of products per page, if option is"
            "used, no pagination used",
            choices=range(0, 101),
            default=100
        )
        self.parser.add_argument(
            "-v",
            "--variant",
            help="Precise this option if you don't want to import variant",
            action="store_false"
        )
        self.parser.add_argument(
            "-i",
            "--image",
            help="Precise this option if you don'want to import images",
            action="store_false"
        )
        self.parser.add_argument(
            "-s",
            "--status",
            choices=["publish", "private", "all"],
            default="all",
            help="Precise the product status you want to import."
            "Default all"
        )
        self.args = self.parser.parse_args()

from .variant import Variant
from .collection import Collection

class Product:
    '''A class to store product that will be write into csv'''
    def __init__(self, **kwargs):
        self.id: str = kwargs.get('id')
        self.title: str = kwargs.get('title')
        self.slug: str = kwargs.get('slug')
        self.summary: str = kwargs.get('summary')
        self.media = kwargs.get('media')
        self.variants: [] = [Variant(**variant) for variant in kwargs.get('variants')]
        self.collections: [] = [Collection(**collection) for collection in kwargs.get('collections')]
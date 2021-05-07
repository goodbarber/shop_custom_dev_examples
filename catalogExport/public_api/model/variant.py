class Variant:
    '''Class representing variant of product in public API'''
    def __init__(self, **kwargs):
        self.id: str = kwargs.get('id')
        self.price: str = kwargs.get('price')
        self.weight: str = kwargs.get('weight')
        self.media = kwargs.get('media')
        self.sku = kwargs.get('sku')
        self.stock = kwargs.get('stock')
        self.compare_at = kwargs.get('compare_at')
        self.options = kwargs.get('options')
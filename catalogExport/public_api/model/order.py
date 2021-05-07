class Order:
    '''Class in order to parse orders from the public API'''
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.created_at = kwargs.get('created_at')
        self.total = kwargs.get('total')
        self.order_num = kwargs.get('order_num')
        self.weight = kwargs.get('weight')
        self.items = kwargs.get('items')
        self.shipping_type = kwargs.get('shipping_type')
        self.shipping_address = kwargs.get('shipping_address')
        self.status = kwargs.get('status')
        self.selected_delivery_slot = kwargs.get('selected_delivery_slot')
class Collection:
    '''Class reprenting collection in public API'''
    def __init__(self, **kwargs):
        self.id: int = kwargs.get('id')
        self.name: str = kwargs.get('name')
    
    def __str__(self):
        return self.name

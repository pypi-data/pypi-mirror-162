
from .resource_abstract import ResourceAbstract

""" Null class """
class Null(ResourceAbstract):
    """ Overwrite the constructor and set data and transformer to None """
    def __init__(self, data, trans = None, resource_key = None):
        super().__init__(data, None, None)

    """ Returns None, a NullResource always returns None """
    def get_data():
        return None

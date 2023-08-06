import re
import sys

""" ResourceAbstract class """
class ResourceAbstract:
    """
        Constructor for the ResourceAbstract
        This allowes to set data and transformer while creating an instance
    """
    def __init__(self, data, trans = None, resource_key = None):
        self.data = data
        self.meta = None
        self.pagination = None
        self.resource_key = resource_key

        transformer, variant = self._separate_ransformer_and_variation(trans)

        self.transformer = transformer
        self.variant = variant

    """ Return the data for this resource """
    def get_data(self):
        return self.data

    """ Returns the transformer set for this resource """
    def get_transformer(self):
        return self.transformer

    """ Set Meta data that will be included when transforming this resource """
    def set_meta(self, meta):
        self.meta = meta

        return self

    """ Returns the metadata """
    def get_meta(self):
        return self.meta

    """ Set pagination information for this resource """
    def set_pagination(self, pagination):
        self.pagination = pagination

        return self

    """ Returns the saved pagination information """
    def get_pagination(self):
        return self.pagination

    """ Set the transformer variant to be used for this resource """
    def set_variant(self, variant):
        if (variant):
            self.variant = variant


        return self

    """ Returns the transformer variant """
    def get_variant(self):
        return self.variant

    def set_resource_key(self, resource_key):
        self.resource_key = resource_key

        return self

    def get_resource_key(self):
        return self.resource_key

    """
        When a transformer string is passed with a variation defined in dot-notation
        we will split the string into transformer and variant
    """
    def _separate_ransformer_and_variation(self, transformer_string):
        # This feature is only available when a string binding is used
        PY3 = sys.version_info[0] == 3

        if (type(transformer_string) is not str):
            return (transformer_string, None )

        regex = "/(.*)\.(.*)/"
        matches = re.match(regex, transformer_string)

        # if the string did not contain a variation use the
        # transformer_string is used and the variation is set to None
        transformer = matches[1] if matches else transformer_string
        variant = matches[2] if matches else None

        return (transformer, variant)

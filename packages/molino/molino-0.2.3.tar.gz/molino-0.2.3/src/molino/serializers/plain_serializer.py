from .serializer_abstract import SerializerAbstract

""" PlainSerializer class """
class PlainSerializer(SerializerAbstract):
    """
        Serialize a collection of data
        The PlainSerializer will just return the data without modification
    """
    def collection(self, data, resource_key = None, depth = 0):
        return data

    """
        Serialize a single item
        The PlainSerializer will return the the data without modification
    """
    def item(self, data, resource_key = None, depth = 0):
        return data

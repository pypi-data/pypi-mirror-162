from .serializer_abstract import SerializerAbstract

""" DataSerializer class """
class DataSerializer(SerializerAbstract):
    """
        Serialize a collection of data
        The DataSerializer will add all data under the 'data' namespace
    """
    def collection(self, data, resource_key = None, depth = 0):
        return { 'data': data }

    """
        Serialize a single item
        The DataSerializer will add the item under the 'data' namespace
    """
    def item(self, data, resource_key = None, depth = 0):
        # if the item is an object, add it to the data property
        if (type(data) is dict):
            return { 'data': data }

        # If the data for this item is not a object, aka. a primitive type
        # we will just return the plain data.
        return data


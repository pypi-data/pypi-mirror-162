""" SerializerAbstract class """
class SerializerAbstract:

    """
        Serialize a collection of data
        You must implement this method in your Serializer
    """
    def collection(self, data, resource_key, depth = 0):
        raise Exception('A Serializer must implement the method collection')

    """
        Serialize a single item of data
        You must implement this method in your Serializer
    """
    def item(self, data, resource_key = None, depth = 0):
        raise Exception('A Serializer must implement the method item');

    """ Serialize a null value """
    def null(self):
        return None

    """ Serialize a meta object """
    def meta(self, meta):
        return { 'meta': meta }

    """ Serialize the pagination meta data """
    def paginator(self, pagination):
        return { 'pagination': pagination }

    """
        Merge included data with the main data for the resource.
        Both includes and data have passed through either the
        'item' or 'collection' method of this serializer.
    """
    def merge_includes(self, data, includes):
        # Include the includes data first.
        # If there is data with the same key as an include, data will take precedence.
        if (self.side_load_includes() == False):
            return { **includes, **data }

        return data;

    def side_load_includes(self):
        return False;

    def include_data(self, data):
        return data;

    def inject_data(self, data, raw_included_data):
        return data;

    def filter_includes(self, included_data, data):
        return included_data;

    def inject_available_include_data(self, data, includes):
        return data;

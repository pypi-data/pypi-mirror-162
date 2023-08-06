
import inspect;
from .resources.item import Item
from .resources.null import Null
from .resources.collection import Collection
from .transformer_abstract import TransformerAbstract

""" Scope class """
class Scope:
    def __init__(self, manager, resource, scopeIdentifier = None):
        self._manager = manager
        self._resource = resource
        self._scope_identifier = scopeIdentifier
        self._parent_scopes = []
        self._available_includes = []

    """ Passes the data through the transformers and serializers and returns the transformed data """
    def json(self):
        # run the transformation on the data
        raw_data, raw_included_data = self._execute_resource_transformers()

        # create a serializer instance
        serializer = self._manager.get_serializer()
        # run the raw data through the serializer
        data = self._serializeResource(serializer, raw_data)

        if (serializer.side_load_includes() and raw_included_data and len(raw_included_data) > 0):
            # Filter out any relation that wasn't requested
            included_data = serializer.include_data(raw_included_data)

            # If the serializer wants to inject additional information
            # about the included resources, it can do so now.
            data = serializer.inject_data(data, raw_included_data)

            if (self.is_root_scope()):
                # If the serializer wants to have a final word about all
                # the objects that are sideloaded, it can do so now.
                included_data = serializer.filter_includes(included_data, data)

            data = { **data, **included_data }

        if (len(self._available_includes) > 0):
            data = serializer.inject_available_include_data(data, self._available_includes)

        # initialize an empty meta object
        meta = {}

        # if the resource is a collection and there is pagination data...
        if (type(self._resource) is Collection and self._resource.get_pagination()):
            # run the pagination data through the serializer and add it to the meta object
            pagination = serializer.paginator(self._resource.get_pagination())
            meta = { **pagination, **meta }

        # if there is custom meta data, add it the our meta object
        if (self._resource.get_meta()):
            meta = serializer.meta(self._resource.get_meta())

        # If any meta data has been added, add it to the response
        if (meta and len(meta.keys) > 0):
            # If the serializer does not support meta data,
            # we just force the data object under a 'data' propert since we can not mix an array with objects
            if (type(data) is dict or type(data) is list):
                data = { 'data': data }

            # merge data with meta data
            data = { **meta, **data }

        # all done, return the transformed data
        return data

    """ Creates a transformer instance and runs data through the transformer """
    def _execute_resource_transformers(self):
        # get a transformer and fetch data from the resource
        transformer = self._resource.get_transformer()
        data = self._resource.get_data()
        transformed_data = []
        included_data = []

        if (data is None or type(self._resource) is Null):
            # If the resource is a null-resource, set data to null without includes
            transformed_data = None
        elif (isinstance(self._resource, Item)):
            # It the resource is an item, run the data through the transformer
            transformed_value, included_value = self._fire_transformer(data, transformer)

            transformed_data = transformed_value

            if (included_value):
                included_data.append(included_value)
        elif (isinstance(self._resource, Collection)):
            # It we have a collection, get each item from the array of data
            # and run each item individually through the transformer
            for value in data:
                transformed_value, included_value = self._fire_transformer(value, transformer)

                transformed_data.append(transformed_value)

                if (included_value):
                    included_data.append(included_value)
        else:
            # If we are here, we have some unknown resource and can not transform it
            raise Exception('This resourcetype is not supported. Use Item or Collection')

        return (transformed_data, included_data)

    """ Runs an object of data through a transformer method """
    def _fire_transformer(self, data, transformer):
        included_data = None
        # get a transformer instance and tranform data
        transformer_instance = self._get_transformer_instance(transformer)
        transformed_data = self._dispatch_to_transformer_variant(transformer_instance, data)

        # if this transformer has includes defined,
        # figure out which includes should be run and run requested includes
        if (self._transformer_has_includes(transformer_instance)):
            included_data = transformer_instance._process_included_resources(self, data)
            transformed_data = self._manager.get_serializer().merge_includes(transformed_data, included_data)

            self._available_includes = [*transformer_instance.default_includes, *transformer_instance.available_includes]


        return (transformed_data, included_data)

    """ Run data through a serializer """
    def _serializeResource(self, serializer, raw_data):
        scopeDepth = len(self.get_scope_array())

        if (type(self._resource ) is Collection):
            return serializer.collection(raw_data, self._resource.get_resource_key(), scopeDepth)

        if (type(self._resource ) is Item):
            return serializer.item(raw_data, self._resource.get_resource_key(), scopeDepth)

        return serializer.null()

    """ Checks if this scope is requested by comparing the current nesting level with the requested includes """
    def _isRequested(self, check_scope_segment):
        # create the include string by combining current level with parent levels
        scope_string = '.'.join([*self.get_scope_array(), check_scope_segment])

        # check if this include was requested. If the include does not occur in the
        # requested includes, we check again, for it may have been requested using
        # snake_case instead of camelCase
        return scope_string in self._manager.get_requested_includes() or scope_string in self._manager.get_requested_includes(True)

    """ Creates and returns a new transformer instance """
    def _get_transformer_instance(self, Transformer):
        # if the transformer is a class, create a new instance
        if (inspect.isclass(Transformer) and issubclass(Transformer, TransformerAbstract)):
            return Transformer()

        if (isinstance(Transformer, TransformerAbstract)):
            return Transformer

        if (callable(Transformer)):
            # if a closure was passed, we create an anonymous transformer class
            # with the passed closure as transform method
            class ClosureTransformer(TransformerAbstract):
                def transform(self, data):
                    return Transformer(data)

            return ClosureTransformer()

        raise Exception('A transformer must be a function or a class extending TransformerAbstract')

    """ Checks if any variants are defined and calls the corresponding transform method """
    def _dispatch_to_transformer_variant(self, transformer_instance, data):
        variant = self._resource.get_variant()

        #  if a variant was defined, we construct the name for the transform mehod
        # otherwise, the default transformer method 'transform' is called
        transformMethodName = f"transform{variant[0,1].uppper()}{variant[1:]}" if variant else 'transform'

        if (callable(getattr(transformer_instance, transformMethodName, None)) is False):
            raise Exception(f"A transformer method '{transformMethodName}' could not be found in '{type(self).__name__}'")

        func = getattr(transformer_instance, transformMethodName)

        # now we call the transformer method on the transformer and return the data
        return func(data)

    """ Check if the used transformer has any includes defined """
    def _transformer_has_includes(self, Transformer):
        default_includes = Transformer.default_includes
        available_includes = Transformer.available_includes

        return len(default_includes) > 0 or len(available_includes) > 0

    """ Set the parent scope identifier """
    def setparent_scopes(self, parent_scopes):
        self._parent_scopes = parent_scopes

    """ Returns the parents scope identifier """
    def get_parent_scopes(self):
        return self._parent_scopes

    """ Get the identifier for this scope """
    def get_scope_identifier(self):
        return self._scope_identifier

    def get_scope_array(self):
        if (self._scope_identifier):
            return [*self._parent_scopes, self._scope_identifier]

        return []

    """ Check, if this is the root scope. """
    def is_root_scope(self):
        return len(self.get_parent_scopes()) == 0

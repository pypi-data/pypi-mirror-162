
from .resources.null import Null
from .resources.item import Item
from .support.snake_case import snake_case
from .resources.collection import Collection
from .resources.resource_abstract import ResourceAbstract


class TransformerAbstract:
    """ Resources that can be included if requested """
    available_includes = []

    """
        List of resources to automatically include
    """
    default_includes = []

    """
        This method is used to transform the data.
        Implementation required
    """

    def transform(self, data):
        raise Exception('You have to implement the method transform or specify a variant when calling the transformer!')

    """ Helper method to transform a collection in includes """
    def collection(self, data, transformer, resource_key = None):
        return Collection(data, transformer, resource_key)

    """ Helper method to transform an object in includes """
    def item(self, data, transformer, resource_key = None):
        return Item(data, transformer, resource_key)

    """ Helper method to return a null resource """
    def null(self):
        return Null()

    """ Processes included resources for this transformer """
    def _process_included_resources(self, parent_scope, data):
        include_data = {}

        # figure out which of the available includes are requested
        resources_to_include = self._figure_out_which_includes(parent_scope)

        # for each include call the include function for the transformer
        for include in resources_to_include:
            resource = self._call_include_function(include, parent_scope, data)

            # if the include uses a resource, run the data through the transformer chain
            if (isinstance(resource, ResourceAbstract)):
                include_data[include] = self._create_child_scope_for(parent_scope, resource, include).json()
            else:
                # otherwise, return the data as is
                include_data[include] = resource

        return include_data

    """ Construct and call the include function """
    def _call_include_function(self, include, parent_scope, data):
        # convert the include name to camelCase
        include = snake_case(include)

        include_name = f"include_{include}"

        if (callable(getattr(self, include_name, None)) == False):
            raise Exception(f"A method called '{include_name}' could not be found in '{type(self).__name__}'")

        func = getattr(self, include_name)

        return func(data)

    """ Returns an array of all includes that are requested """
    def _figure_out_which_includes(self, parent_scope):
        includes = self.default_includes
        requested_available_includes = list(filter(lambda i: parent_scope._isRequested(i), self.available_includes))

        return [*includes, *requested_available_includes]

    """ Create a new scope for the included resource """
    def _create_child_scope_for(self, parent_scope, resource, include):
        # create a new scope
        from .scope import Scope;

        child_scope = Scope(parent_scope._manager, resource, include)

        # get the scope for this transformer
        scope_array = [*parent_scope.get_parent_scopes()]

        if (parent_scope.get_scope_identifier()):
            identifier = parent_scope.get_scope_identifier()

            if (identifier):
                scope_array.append(identifier)

        # set the parent scope for the new child scope
        child_scope.setparent_scopes(scope_array)

        return child_scope
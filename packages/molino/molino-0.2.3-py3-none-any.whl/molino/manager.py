from .scope import Scope
from .support.snake_case import snake_case
from .serializers.data_serializer import DataSerializer
from .serializers.plain_serializer import PlainSerializer
from .serializers.json_api_serializer import JsonApiSerializer
from .serializers.sld_data_serializer import SldDataSerializer

""" Manager class """
class Manager:
    def __init__(self):
        self._recursion_limit = 10
        self.serializer = None
        self.requested_includes = []
        self._recursion_limit = 10

    """ Create a Scope instance for the resource """
    def create_data(self, resource):
        self._setIncludesFromRequest()

        return Scope(self, resource)

    """ Returns the requested includes. An optional parameter converts snake_case.
        includes to standardized snake_case
    """
    def get_requested_includes(self, transform_snake_case = False):
        if (transform_snake_case is False):
            return self.requested_includes

        def callback(i):
            return snake_case(i)

        includes = '.'.join(map(callback, [*self.requested_includes]))

        return includes

    """ Parses an include string or array and constructs an array of all requested includes """
    def parse_includes(self, includes):
        self.requested_includes = []

        # if a string is passed, split by comma and return an array
        if (type(includes) is str):
            includes = list(map(lambda value: value.strip(), includes.split(',')))

        # if it is not an array, we can not parse it at this point
        if (type(includes) is not list == True):
            raise (f"The parse_includes() method expects a string or an array. {type(includes)} given")

        # sanitize the includes
        includes = list(map(lambda i: self._guard_against_to_deep_recursion(i), includes))

        # add all includes to the internal set
        for value in includes:
            if (value not in self.requested_includes):
                self.requested_includes.append(value)

        self._auto_include_parents()

    """ Allowes setting a custom recursion limit """
    def set_recursion_limit(self, limit):
        self._recursion_limit = limit

        return self

    """ Create a serializer """
    def set_serializer(self, serializer):
        if (type(serializer) is str):
            if (serializer == 'data'):
                serializer = DataSerializer()
            elif (serializer == 'sld'):
                serializer = SldDataSerializer()
            elif (serializer == 'plain'):
                serializer = PlainSerializer()
            elif (serializer == 'json-api'):
                serializer = JsonApiSerializer()
            else:
                raise Exception(f"No data serializer for {serializer}")

        self.serializer = serializer

    """ Get an instance if the serializer, if not set, use setting from the config """
    def get_serializer(self):
        if (self.serializer is None):
            self.set_serializer(PlainSerializer())

        return self.serializer

    """ To prevent to many recursion, we limit the number of nested includes allowed """
    def _guard_against_to_deep_recursion(self, include):
        return '.'.join(include.split('.')[0:self._recursion_limit])

    """ Add all the resources along the way to a nested include """
    def _auto_include_parents(self):
        parsed = []

        # for each resource that is requested
        for include in self.requested_includes:
            # we split it by '.' to get the recursions
            nested = include.split('.')

            # Add the first level to the includes
            part = nested[0:1][0]
            parsed.append(part)

            # if there are more nesting levels,
            # add each level to the includes
            for segment in nested[1:]:
                part += f".{segment}"
                parsed.append(part)

        # add all parsed includes to the set of requested includes
        for value in parsed:
            if (value not in self.requested_includes):
                self.requested_includes.append(value)

    """ Parses the request object from the context and extracts the requested includes """
    def _setIncludesFromRequest(self):
        # get all get parameters from the request
        # if the 'include' parameter is set, pass it the the parse method
        params = {}

        if ('include' in params):
            self.parse_includes(params.include)
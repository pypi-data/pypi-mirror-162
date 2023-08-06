from .serializer_abstract import SerializerAbstract

class JsonApiSerializer(SerializerAbstract):
    def __init__(self, base_url = None):
        super()
        self.base_url = None
        self.root_objects = []
        self.base_url = base_url

    def collection(self, data, resource_key = None, depth = 0):
        resources = []

        for resource in data:
            item = self.item(resource, resource_key, depth)

            resources.append(item['data'])

        return { 'data': resources }

    def item(self, data, resource_key = None, depth = 0):
        id = self.get_id_from_data(data)
        custom_links = None

        resource = {
            'data': {
                'type': resource_key,
                'id': id,
                'attributes': data,
            }
        }

        del resource['data']['attributes']['id']

        if ('links' not in resource['data']['attributes']):
            custom_links = data['links'] if 'links' in data else None

            if ('links' in resource['data']['attributes']):
                del resource['data']['attributes']['links']

        if ('meta' not in resource['data']['attributes']):
            resource['data']['meta'] = data['meta'] if 'meta' in data else None

            if ('meta' in resource['data']['attributes']):
                del resource['data']['attributes']['meta']

        if ('attributes' not in resource['data']):
            resource['data']['attributes'] = {}

        if (self.should_include_links()):
            resource['data']['links'] = {
                'self': '' f"{self.base_url}/{resource_key}/{id}",
            }

            if (custom_links):
                resource['data']['links'] = { **resource['data']['links'], **custom_links };

        return resource

    def paginator(sel, paginator):
        currentPage = paginator.getCurrentPage()
        lastPage = paginator.getLastPage()

        pagination = {
            'total': paginator.getTotal(),
            'count': paginator.getCount(),
            'per_page': paginator.getPerPage(),
            'current_page': currentPage,
            'total_pages': lastPage,
        }

        pagination['links'] = {}
        pagination['links']['self'] = paginator.getUrl(currentPage)
        pagination['links']['first'] = paginator.getUrl(1)

        if (currentPage > 1):
            pagination['links']['prev'] = paginator.getUrl(currentPage - 1)

        if (currentPage < lastPage):
            pagination['links']['next'] = paginator.getUrl(currentPage + 1)

        pagination['links']['last'] = paginator.getUrl(lastPage)

        return { 'pagination': pagination }

    def meta(self, meta):
        if (meta is None or len(meta) == 0):
            return {}

        result = {
            'meta': meta
        }

        if (result['meta'] and result['meta']['pagination']):
            result['links'] = result['meta']['pagination']['links']

            del result['meta']['pagination']['links']

        return result

    def null(self):
        return { 'data': None }

    def include_data(self, data):
        serialized_data, linked_ids = self.pull_out_nested_included_data(data)

        for value in data:
            for include_object in value.values():
                if (self.is_primitive(include_object)):
                    continue

                include_objects = self.create_include_objects(include_object)
                serialized_data, linked_ids = self.serialize_included_objects_with_cache_key(include_objects, linked_ids, serialized_data)

        return {} if serialized_data is None or len(serialized_data) == 0 else { 'included': serialized_data }

    def side_load_includes(self):
        return True

    def inject_data(self, data, raw_included_data):
        if (self.is_primitive(data) or self.is_null(data) or self.is_empty(data)):
            return data

        relationships = self.parse_relationships(raw_included_data)

        if (len(relationships) > 0):
            data = self.fill_relationships(data, relationships)

        return data

    """
        Hook to manipulate the final sideloaded includes.
        The JSON API specification does not allow the root object to be included
        into the sideloaded `included`-array. We have to make sure it is
        filtered out, in case some object links to the root object in a
        relationship.
    """
    def filter_includes(self, included_data, data):
        if ('included' not in included_data):
            return included_data

        # Create the root_objects
        self.create_root_objects(data)
        # Filter out the root objects
        filtered_includes = list(filter(lambda value: self.filter_root_object(value), included_data['included']))
        # Reset array indizes
        included_data['included'] = filtered_includes

        return included_data

    def get_mandatory_fields(self):
        return ['id']

    """ Filter function to del root objects from array. """
    def filter_root_object(self, object):
        return self.is_root_object(object) is False

    """ Set the root objects of the JSON API tree. """
    def set_root_objects(self, objects = []):
        self.root_objects = list(map(lambda object: f"{object['type']}:{object['id']}", objects))

    """ Determines whether an object is a root object of the JSON API tree. """
    def is_root_object(self, object):
        object_key = f"{object['type']}:{object['id']}"

        return object_key in self.root_objects

    def is_collection(self, data):
        return self.is_primitive(data) is False and 'data' in data and type(data['data']) is list

    def is_null(self, data):
        return self.is_primitive(data) is False and ('data' in data and type(data['data']) is None) or (type(data) is list and (len(data['data']) == 0 or data['data'][0] is None))

    def is_empty(self, data):
        return self.is_primitive(data) is False and 'data' in data and type(data['data']) is list and len(data['data']) > 0 and type(data['data'][0]) is dict and len(data['data'][0]) == 0

    def is_primitive(self, data):
        return type(data) is not dict and type(data) is not list

    def fill_relationships(self, data, relationships):
        if (self.is_collection(data)):
            for index in relationships:
                relationship = relationships[index]
                data = self.fill_relationship_as_collection(data, relationship, index)
        else: # Single resource
            for index in relationships:
                relationship = relationships[index]
                data = self.fill_relationship_as_single_resource(data, relationship, index)

        return data

    def parse_relationships(self, included_data):
        relationships = {}

        for index, inclusion in enumerate(included_data):
            for include_key, include_object in inclusion.items():
                if (self.is_null(include_object) or self.is_empty(include_object)):
                    continue

                relationships = self.build_relationships(include_key, relationships, include_object, index)

                if (type(included_data[0][include_key]) is dict and 'meta' in included_data[0][include_key]):
                    relationships[include_key][0]['meta'] = included_data[0][include_key]['meta']

        return relationships

    def get_id_from_data(self, data):
        if ('id' not in data == True):
            raise Exception('JSON API resource objects MUST have a valid id')

        return data['id']

    """ Keep all sideloaded inclusion data on the top level. """
    def pull_out_nested_included_data(self, data):
        included_data = []
        linked_ids = {}

        for value in data:
            for include_object in value.values():
                if (type(include_object) is dict and 'included' in include_object):
                    included_data, linked_ids = self.serialize_included_objects_with_cache_key(include_object['included'], linked_ids, included_data)

        return (included_data, linked_ids)

    """ Whether or not the serializer should include `links` for resource objects. """
    def should_include_links(self):
        return self.base_url is not None

    """ Check if the objects are part of a collection or not """
    def create_include_objects(self, include_object):
        if self.is_collection(include_object):
            return include_object['data']

        return [include_object['data']]

    """ Sets the root_objects, either as collection or not. """
    def create_root_objects(self, data):
        if (self.is_collection(data)):
            self.set_root_objects(data['data'])
        else:
            self.set_root_objects([data['data']])

    """ Loops over the relationships of the provided data and formats it """
    def fill_relationship_as_collection(self, data, relationship, key):
        for index in relationship:
            relationship_data = relationship[index]

            if ('relationships' not in data['data'][index]):
                data['data'][index]['relationships'] = {}

            data['data'][index]['relationships'][key] = relationship_data

        return data

    def fill_relationship_as_single_resource(self, data, relationship, key):
        if ('relationships' not in data['data']):
            data['data']['relationships'] = {}

        data['data']['relationships'][key] = relationship[0]

        return data

    def build_relationships(self, include_key, relationships, include_object, key):
        relationship = None
        relationships = self.add_include_key_to_relations_if_not_set(include_key, relationships)

        if (self.is_null(include_object)):
            relationship = self.null()
        elif (self.is_empty(include_object)):
            relationship = {
                'data': [],
            }
        elif (self.is_primitive(include_object)):
            relationship = {
                'data': {
                    'type': include_key,
                    'value': include_object
                },
            }
        elif (self.is_collection(include_object)):
            relationship = { 'data': [] }
            relationship = self.add_included_data_to_relationship(include_object, relationship)
        else:
            relationship = {
                'data': {
                    'type': include_object['data']['type'],
                    'id': include_object['data']['id'],
                },
            }

        relationships[include_key][key] = relationship

        return relationships

    def add_include_key_to_relations_if_not_set(self, include_key, relationships):
        if (include_key not in relationships):
            relationships[include_key] = {}

        return relationships

    def add_included_data_to_relationship(self, include_object, relationship):
        for obj in include_object['data']:
            relationship['data'].append({
                'type': obj['type'],
                'id': obj['id'],
            })

        return relationship

    def inject_available_include_data(self, data, available_includes):
        if (self.should_include_links() is False):
            return data

        if (self.is_collection(data)):
            def callback(resource):
                for relationship_key in available_includes:
                    resource = self.add_relationship_links(resource, relationship_key)

                return resource

            data['data'] = list(map(callback, data['data']))
        else:
            for relationship_key in available_includes:
                data['data'] = self.add_relationship_links(data['data'], relationship_key)

        return data

    """ Adds links for all available includes to a single resource. """
    def add_relationship_links(self, resource, relationship_key):
        if ('relationships' not in resource):
            resource['relationships'] = {}

        if (relationship_key not in resource['relationships']):
            resource['relationships'][relationship_key] = {}

        links = {
            'links': {
                'self': f"{self.base_url}/{resource['type']}/{resource['id']}/relationships/{relationship_key}",
                'related': f"{self.base_url}/{resource['type']}/{resource['id']}/{relationship_key}",
            }
        }

        resource['relationships'][relationship_key] = { **links, **resource['relationships'][relationship_key] }

        return resource

    def serialize_included_objects_with_cache_key(self, include_objects, linked_ids, serialized_data):
        for obj in include_objects:
            include_type = obj['type']
            include_id = obj['id']
            cache_key = f"{include_type}:{include_id}"

            if (cache_key not in linked_ids):
                serialized_data.append(obj)
                linked_ids[cache_key] = obj


        return (serialized_data, linked_ids)

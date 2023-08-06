from .manager import Manager
from .resources.null import Null
from .resources.item import Item
from .resources.collection import Collection

""" Forge class """
class Forge:
  """
    Create a new Forge instance.
    An instance of Manager has to be passed
  """
  def __init__(self, manager: Manager):
    self._manager = manager
    self._data = None
    self._data_type = None
    self._transformer = None
    self._variant = None
    self._resource_key = None
    self._pagination = None
    self._meta = None

  """
    Creates a new instance of Forge
    Data and transformer can optionally be passed or set via setters in the instance.
  """
  @classmethod
  def make(cls, data = None, transformer = None, resource_key = None):
    # create an instance of Forge and pass a new instance of Manager
    instance = cls(Manager())

    # initialize data and transformer properties
    dataType = instance._determine_data_type(data)

    instance._set_data(dataType, data, resource_key)

    if (transformer):
      instance.with_transformer(transformer)

    # return the instance for the fluid interface
    return instance

  """
    Add a collection of data to be transformed.
    If a transformer is passed, the fluid interface is terminated
  """
  def collection(self, data, transformer = None, resource_key = None):
    self._set_data('Collection', data, resource_key)

    if (transformer):
      self.with_transformer(transformer)

    return self

  """
    Add data that should be transformed as a single item.
    If a transformer is passed, the fluid interface is terminated
  """
  def item(self, data, transformer = None, resource_key = None):
    self._set_data('Item', data, resource_key)

    if (transformer):
      self.with_transformer(transformer)

    return self

  """ Sets data to Null """
  def null(self):
    self._set_data('Null', None)

    return self

  """
    Add a collection of data to be transformed.
    Works just like collection but requires data to be a lucid paginated model.
    If a transformer is passed, the fluid interface is terminated
  """
  def paginate(self, data, transformer = None, resource_key = None):
    self._set_data('Collection', data.rows)

    # extract pagination data
    paginationData = data.pages

    # ensure the pagination keys are integers
    for key in paginationData.keys():
      paginationData[key] = int(paginationData[key])

    # set pagination data
    self._pagination = paginationData

    if (transformer):
      self.with_transformer(transformer)

    return self

  """ Add additional meta data to the object under transformation """
  def meta(self, meta):
    return self.with_meta(meta)

  """ Add additional meta data to the object under transformation """
  def with_meta(self, meta):
    self._meta = meta

    return self

  """ Set the transformer """
  def transformer(self, transformer):
    return self.with_transformer(transformer)

  """ Set the transformer """
  def with_transformer(self, transformer):
    self._transformer = transformer

    return self

  """ Set the transformer variant """
  def variant(self, variant):
    return self.with_variant(variant)

  """ Set the transformer variant """
  def with_variant(self, variant):
    self._variant = variant

    return self

  """
    Additional resources that should be included and that are defined as
    'available_includes' on the transformer.
  """
  def include(self, include):
    self._manager.parse_includes(include)

    return self

  """
    Additional resources that should be included and that are defined as
    'available_includes' on the transformer.
  """
  def including(self, include):
    return self.include(include)

  """ Set the serializer for this transformation. """
  def serializer(self, serializer):
    return self.with_serializer(serializer)

  """
    Alias for 'serializer'
  """
  def with_serializer(self, serializer):
    self._manager.set_serializer(serializer)

    return self

  def get_manager(self):
    return self._manager

  """ Terminates the fluid interface and returns the transformed data. """
  def json(self):
    return self._create_data().json()

  def _set_data(self, dataType, data, resource_key = None):
    self._data = data
    self._data_type = dataType
    self._pagination = None
    self._resource_key = resource_key

    return self

  """ Helper function to set resource on the manager """
  def _create_data(self):
    return self._manager.create_data(self._get_resource())

  """ Create a resource for the data and set meta and pagination data """
  def _get_resource(self):
    Resource = None

    if (self._data_type == 'Collection'):
        Resource = Collection
    elif (self._data_type == 'Item'):
        Resource = Item
    elif (self._data_type == 'Null'):
        Resource = Null

    resource_instance = Resource(self._data, self._transformer)

    resource_instance.set_meta(self._meta)
    resource_instance.set_pagination(self._pagination)
    resource_instance.set_variant(self._variant)
    resource_instance.set_resource_key(self._resource_key)

    return resource_instance

  """ Determine resource type based on the type of the data passed """
  def _determine_data_type(self, data):
    if (data is None):
      return 'Null'

    if (type(data) is list):
      return 'Collection'

    return 'Item'
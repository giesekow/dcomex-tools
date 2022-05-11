import enum, os
from .data import DataType, ScalarType
from tinydb import TinyDB, Query


class PluginType(enum.Enum):
  EXECUTABLE = 'exec'
  PYTHON = 'python'

  @classmethod
  def get_item_by_value(cls, value):
    map_data = cls._member_map_
    
    for d in map_data:
      if value == map_data[d].value:
        return map_data[d]
    
    return None

class PluginGroupType(enum.Enum):
  VIEWER = 'viewer'
  PROCESSING = 'processing'

  @classmethod
  def get_item_by_value(cls, value):
    map_data = cls._member_map_
    
    for d in map_data:
      if value == map_data[d].value:
        return map_data[d]
    
    return None

class PluginInput:
  def __init__(self, name: str, dtype: DataType, scalar_type: ScalarType, optional: bool) -> None:
    self.name = name
    self.dtype = dtype
    self.scalar_type = scalar_type
    self.optional = optional

class PluginOutput:
  def __init__(self, name: str, dtype: DataType, scalar_type: ScalarType) -> None:
    self.name = name
    self.dtype = dtype
    self.scalar_type = scalar_type

class PluginManager:
  def __init__(self) -> None:
    plugin_path = os.path.join(os.path.expanduser("~"), ".dcomex", "plugins")
    os.makedirs(plugin_path, exist_ok=True)
    self.db = TinyDB(os.path.join(plugin_path, 'plugins.json'))
    self.plugins = self.db.table("plugins")
    self.groups = self.db.table("groups")

  def get_plugins(self):
    items = self.plugins.all()
    return items

  def get_plugin(self, doc_id):
    item = self.plugins.get(doc_id=doc_id)
    return item

  def find_plugin_by_name(self, name):
    q = Query()
    items =  self.plugins.search(q.name==name)
    return items

  def insert_plugin(self, data):
    q = Query()
    items =  self.plugins.search(q.name==data.get("name"))
    if len(items) > 0:
      return False, f"Plugin with name '{data.get('name')}' already exists"

    group = data.get("group")
    if not group is None and type(group) == str:
      grps = self.find_group_by_name(group)
      if len(grps) > 0:
        data["group"] = grps[0].doc_id
      else:
        return False, f"No plugin group with name '{group}' exist!"

    self.plugins.insert(data)
    return True, ""

  def remove_plugin(self, idx):
    self.plugins.remove(doc_ids=[idx])

  def update_plugin(self, data, idx):
    self.plugins.update(data, doc_ids=[idx])

  def find_plugin_by_group(self, group_id):
    q = Query()
    return self.plugins.search(q.group==group_id)

  def get_groups(self):
    items = self.groups.all()
    return items

  def get_group(self, doc_id):
    item = self.groups.get(doc_id=doc_id)
    return item

  def insert_group(self, data):
    q = Query()
    items =  self.groups.search(q.name==data.get("name"))
    if len(items) > 0:
      return False, f"Group with name '{data.get('name')}' already exists"

    self.groups.insert(data)

  def remove_group(self, idx):
    self.groups.remove(doc_ids=[idx])

  def update_group(self, data, idx):
    self.groups.update(data, doc_ids=[idx])

  def find_group_by_type(self, g_type):
    q = Query()
    return self.groups.search(q.type==g_type)

  def find_group_by_name(self, name):
    q = Query()
    return self.groups.search(q.name==name)
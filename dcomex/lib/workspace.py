import json, traceback
from .utils import json_default, json_object_hook
from .data import DataType

class Workspace:
  def __init__(self) -> None:
    self.data = []
    self.last_filename = None

  def load(self, filename):
    self.last_filename = filename
    with open(filename, "r") as json_file:
      data = json.load(json_file, object_hook=json_object_hook)
      self.data = data.get("data", [])

  def get_data_type(self, dtype, subtype=None, isMultiple=False) -> list:
    data = []
    ism = isMultiple if not isMultiple is None else False

    for d in self.data:
      dism = d.get("ismultiple", False)
      if dism is None:
        dism = False
      if d.get("type") == dtype and ((subtype is None) or (d.get("subtype") == subtype)) and (ism == dism):
        data.append(d)
    return data

  def save(self, filename=None):
    data = {
      "data": self.data
    }

    if not self.last_filename is None:
      if filename is None:
        filename = self.last_filename

    if filename is None:
      return "filename is required!"
    
    self.last_filename = filename
    with open(filename, "w") as json_file:
      try:
        json.dump(data, json_file, default=json_default)
        return True
      except Exception as ex:
        et = traceback.format_exc()
        print(f"Error: {ex}")
        print(f"Error trace: {et}")
        return str(ex)


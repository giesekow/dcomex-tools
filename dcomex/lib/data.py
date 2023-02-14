import enum, os

class DataType(enum.Enum):
  IMAGE = 'image'
  JSON = 'json'
  TEXT = 'text'
  MESH = 'mesh'
  CSV = 'csv'
  SCALAR = 'scalar'
  FILE = 'file'
  FOLDER = 'folder'

  @classmethod
  def get_item_by_value(cls, value):
    map_data = cls._member_map_
    
    for d in map_data:
      if value == map_data[d].value:
        return map_data[d]
    
    return None

class ImageType(enum.Enum):
  NIFTI = 'nifti'
  DICOM = 'dicom'

  @classmethod
  def get_item_by_value(cls, value):
    map_data = cls._member_map_
    
    for d in map_data:
      if value == map_data[d].value:
        return map_data[d]
    
    return None
  
class ScalarType(enum.Enum):
  INT = 'int'
  STR = 'str'
  FLOAT = 'float'
  BOOL = 'bool'
  DATETIME = 'datetime'
  OTHERS = 'others'

  @classmethod
  def get_item_by_value(cls, value):
    map_data = cls._member_map_
    
    for d in map_data:
      if value == map_data[d].value:
        return map_data[d]
    
    return None

class Data:
  def __init__(self, name: str, dtype: DataType, is_array: bool, file_fmt: str, file_path: str, scalar_dtype: ScalarType) -> None:
    self.name = name
    self.dtype = dtype
    self.is_array = is_array
    self.file_fmt = file_fmt
    self.file_path = os.path.join(file_path)
    self.scalar_dtype = scalar_dtype
    self.items = []
  
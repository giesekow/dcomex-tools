from PyQt5.QtCore import QAbstractTableModel, Qt, QSize
from datetime import datetime

class TableModel(QAbstractTableModel):
  def __init__(self, data, headers=None, parent=None) -> None:
    super().__init__(parent)
    self._data = data
    self._headers = headers

  def data(self, index, role):
    if role == Qt.DisplayRole:
      # See below for the nested-list data structure.
      # .row() indexes into the outer list,
      # .column() indexes into the sub-list
      value = self._data[index.row()][index.column()]
      if isinstance(value, datetime):
        return value.isoformat()

      if isinstance(value, list):
        return str(value)
      
      return value

  def rowCount(self, index=None):
    # The length of the outer list.
    return len(self._data)

  def columnCount(self, index=None):
    # The following takes the first sub-list, and returns
    # the length (only works if all rows are an equal length)
    if not self._headers is None:
      return len(self._headers)
      
    if len(self._data) > 0:
      return len(self._data[0])
    
    return 0

  def headerData(self, section: int, orientation: Qt.Orientation, role: int=Qt.DisplayRole):
    if orientation == Qt.Horizontal:
      if not self._headers is None:
        if len(self._headers) > section:
          head = self._headers[section]

          if isinstance(head, dict):
            if role == Qt.DisplayRole:
              return head.get("text")
            if role == Qt.SizeHintRole:
              if "width" in head:
                return head.get("width")

          else:
            if role == Qt.DisplayRole:
              return str(head)
            if role == Qt.SizeHintRole:
              return QSize(400, 30)

      return str(section + 1)

    if orientation == Qt.Vertical:
      if role == Qt.DisplayRole:
        return str(section + 1)
      
    return super().headerData(section, orientation, role)
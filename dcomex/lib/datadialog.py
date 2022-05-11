import typing, copy
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QTableView, QDialog
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QListWidget
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDateTimeEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from .data import DataType, ScalarType, TableModel, ImageType
from .workspace import Workspace

class DataDialog(QDialog):
  def __init__(self, workspace: Workspace, parent: typing.Optional[QWidget] = None) -> None:
    super().__init__(parent)
    self._workspace = workspace
    self._data = copy.deepcopy(self._workspace.data)
    self.setMinimumSize(700, 500)
    self.setWindowTitle("Data Store")
    self.setWindowModality(Qt.WindowModality.ApplicationModal)
    self.build_ui()

  def build_ui(self):
    self._layout = QVBoxLayout()
    self.build_table()
    self.build_buttons()
    self.setLayout(self._layout)

  def build_table(self):
    items, headers = self.load_table_data()
    self.model = TableModel(items, headers, self)
    self.view = QTableView()
    self.view.setModel(self.model)
    self._layout.addWidget(self.view)

  def save_current_data(self, data, index=None):
    if index is None:
      self._data.append(data)
    else:
      self._data[index] = data

    self.refresh_table()

  def refresh_table(self):
    items, headers = self.load_table_data()
    self.model.deleteLater()
    self.model = TableModel(data=items, headers=headers, parent=self)
    self.view.setModel(self.model)

  def load_table_data(self):
    _data = self._data
    items = []
    for d in _data:
      items.append([d.get("name"), d.get("type"), d.get("subtype"), d.get("value")])

    headers = ["Name", "Type", "Sub Type", "Value"]
    return items, headers

  def build_buttons(self):
    widget = QWidget(self)
    layout = QHBoxLayout()

    btn_remove_selected = QPushButton("Remove Selected", widget)
    btn_remove_selected.clicked.connect(self.on_remove_selected_clicked)
    layout.addWidget(btn_remove_selected)

    btn_edit_selected = QPushButton("Edit Selected", widget)
    btn_edit_selected.clicked.connect(self.on_edit_selected_clicked)
    layout.addWidget(btn_edit_selected)

    btn_add_file = QPushButton("Add File", widget)
    btn_add_file.clicked.connect(self.on_add_file_clicked)
    layout.addWidget(btn_add_file)

    '''
    btn_add_scalar = QPushButton("Add Scalar", widget)
    btn_add_scalar.clicked.connect(self.on_add_scalar_clicked)
    layout.addWidget(btn_add_scalar)
    '''

    layout.addStretch(1)

    btn_close = QPushButton("Close", widget)
    btn_close.clicked.connect(self.close)
    layout.addWidget(btn_close)

    btn_save = QPushButton("Save", widget)
    btn_save.clicked.connect(self.save_data)
    layout.addWidget(btn_save)

    widget.setLayout(layout)
    self._layout.addWidget(widget)

  def save_data(self):
    self._workspace.data = self._data
    self.show_msg("Data successfully updated!")

  def on_add_file_clicked(self):
    self.build_file_dialog()

  def on_add_scalar_clicked(self):
    self.build_scalar_dialog()

  def on_remove_selected_clicked(self):
    result = QMessageBox.question(self, "Remove Item!", "Are you sure you want to remove item(s) ?",QMessageBox.Yes| QMessageBox.No)
    if result == QMessageBox.Yes:
      indexes = self.view.selectedIndexes()
      idxs = []
      for idx in indexes:
        idxs.append(idx.row())
      
      idxs = sorted(idxs, reverse=True)
      for idx in idxs:
        self._data.pop(idx)
      
      self.refresh_table()

  def on_edit_selected_clicked(self):
    indexes = self.view.selectedIndexes()
    if len(indexes) > 0:
      index = indexes[0].row()
      data = self._data[index]
      if not isinstance(data, dict):
        return

      dtype = data.get("type")
      if dtype != "scalar":
        self.build_file_dialog(data, index)
      elif dtype == "scalar":
        self.build_scalar_dialog(data, index)

  def show_msg(self, text, detail="", title=""):
    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setDetailedText(detail)
    msg.exec()

  def show_error(self, text, detail="", title=""):
    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setDetailedText(detail)
    msg.exec()

  def build_file_dialog(self, dataInfo=None, index=None):
    dialog = QDialog(self)
    dialog.setMaximumWidth(700)
    layout = QVBoxLayout()

    name_layout = QHBoxLayout()
    name_label = QLabel("Variable Name", dialog)
    name_field = QLineEdit(dialog)
    name_layout.addWidget(name_label)
    name_layout.addWidget(name_field)
    layout.addLayout(name_layout)

    file_type_layout = QHBoxLayout()
    file_type_label = QLabel("Type", dialog)
    file_type_field = QComboBox(dialog)
    file_type_layout.addWidget(file_type_label)
    file_type_layout.addWidget(file_type_field)
    layout.addLayout(file_type_layout)

    for i_type in DataType:
      if i_type != DataType.SCALAR:
        file_type_field.addItem(i_type.name, userData=i_type)

    type_layout = QHBoxLayout()
    type_label = QLabel("File Format", dialog)
    type_field = QComboBox(dialog)
    type_layout.addWidget(type_label)
    type_layout.addWidget(type_field)
    layout.addLayout(type_layout)
    for i_type in ImageType:
      type_field.addItem(i_type.name, userData=i_type)

    
    multi_field = QCheckBox("Is &List", dialog)
    layout.addWidget(multi_field)

    btn_select = QPushButton("Select file", dialog)
    selected_file = QLabel("", dialog)
    layout.addWidget(btn_select)
    layout.addWidget(selected_file)


    files_layout = QVBoxLayout()
    files_label = QLabel("Files", dialog)
    files_field = QListWidget(dialog)
    files_field.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
    files_layout.addWidget(files_label)
    files_layout.addWidget(files_field)
    layout.addLayout(files_layout)
    layout.addStretch(1)

    btn_layout = QHBoxLayout()
    btn_add_file = QPushButton("Add", dialog)
    btn_remove_file = QPushButton("Remove", dialog)
    btn_insert_file = QPushButton("Insert", dialog)
    btn_clear_file = QPushButton("Clear", dialog)
    btn_save = QPushButton("Save", dialog)
    btn_cancel = QPushButton("Cancel", dialog)
    btn_remove_file.setEnabled(False)
    btn_insert_file.setEnabled(False)
    btn_clear_file.setEnabled(False)

    btn_layout.addWidget(btn_add_file)
    btn_layout.addWidget(btn_insert_file)
    btn_layout.addWidget(btn_remove_file)
    btn_layout.addWidget(btn_clear_file)
    btn_layout.addStretch(1)
    btn_layout.addWidget(btn_cancel)
    btn_layout.addWidget(btn_save)
    layout.addLayout(btn_layout)

    def on_multi_checked(s):
      files_label.setVisible(s > 0)
      files_field.setVisible(s > 0)
      btn_select.setVisible(s == 0)
      selected_file.setVisible(s == 0)
      btn_add_file.setVisible(s > 0)
      btn_remove_file.setVisible(s > 0)
      btn_insert_file.setVisible(s > 0)
      btn_clear_file.setVisible(s > 0)

    multi_field.stateChanged.connect(on_multi_checked)
    multi_field.setChecked(True)
    multi_field.setChecked(False)

    btn_cancel.clicked.connect(dialog.close)
    
    file_dialog: QFileDialog = None

    def select_file():
      file_dialog = QFileDialog(dialog)
      f_type = type_field.currentText()
      ft_type = file_type_field.currentText()

      if ft_type == DataType.IMAGE.name:  
        if f_type == ImageType.DICOM.name:
          file_dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)
        else:
          file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
          file_dialog.setNameFilter("Images (*.nii *.nii.gz *.png *.jpg *.jpeg)")
      elif ft_type == DataType.FOLDER.name:
        file_dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)
      else:
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        filters = {
          DataType.JSON.name: "JSON (*.json)",
          DataType.TEXT: "TEXT (*.txt)",
          DataType.CSV: "CSV (*.csv *.tsv)",
        }
        if ft_type in filters:
          file_dialog.setNameFilter(filters.get(ft_type))

      if file_dialog.exec():
        filenames = file_dialog.selectedFiles()
        selected_file.setText(filenames[0])

    def add_file():
      file_dialog = QFileDialog(dialog)
      f_type = type_field.currentText()
      ft_type = file_type_field.currentText()

      if ft_type == DataType.IMAGE.name:  
        if f_type == ImageType.DICOM.name:
          file_dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)
        else:
          file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
          file_dialog.setNameFilter("Images (*.nii *.nii.gz *.png *.jpg *.jpeg)")
      elif ft_type == DataType.FOLDER.name:
        file_dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)
      else:
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        filters = {
          DataType.JSON.name: "JSON (*.json)",
          DataType.TEXT: "TEXT (*.txt)",
          DataType.CSV: "CSV (*.csv *.tsv)",
        }
        if ft_type in filters:
          file_dialog.setNameFilter(filters.get(ft_type))

      file_dialog
      if file_dialog.exec():
        filenames = file_dialog.selectedFiles()
        for filename in filenames:
          files_field.addItem(filename)

    def insert_file():
      file_dialog = QFileDialog(dialog)
      f_type = type_field.currentText()
      if f_type == ImageType.DICOM.name:
        file_dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)
      else:
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.nii *.nii.gz *.png *.jpg *.jpeg)")

      if file_dialog.exec():
        filenames = file_dialog.selectedFiles()
        index = files_field.selectedIndexes()
        idx = 0
        if len(index) > 0:
          idx = index[0].row()
        
        files_field.insertItems(idx, filenames)

    def remove_file():
      result = QMessageBox.question(self, "Remove Item!", "Are you sure you want to remove item(s) ?",QMessageBox.Yes| QMessageBox.No)
      if result == QMessageBox.Yes:
        indexes = files_field.selectedIndexes()
        idxs = []
        for idx in indexes:
          idxs.append(idx.row())
        
        idxs = sorted(idxs, reverse=True)
        for idx in idxs:
          files_field.takeItem(idx)

    def clear_file():
      files_field.clear()

    def file_selection_changed():
      has_selection = len(files_field.selectedIndexes()) > 0
      btn_insert_file.setEnabled(has_selection)
      btn_remove_file.setEnabled(has_selection)

    def file_type_changed(idx):
      f_type = file_type_field.currentText()
      type_field.setVisible(f_type == DataType.IMAGE.name)
      type_label.setVisible(f_type == DataType.IMAGE.name)
        
    def save_dialog():
      name = name_field.text()
      if name.strip() == "":
        self.show_error("variable name required!")
        return

      value = None
      if multi_field.isChecked():
        value = []
        for i in range(files_field.count()):
          itm = files_field.item(i)
          value.append(itm.text())
      else:
        value = selected_file.text()

      data = {
        "name": name,
        "type": file_type_field.currentData().value,
        "subtype": type_field.currentData().value if file_type_field.currentData().value == "image" else "",
        "ismultiple": multi_field.isChecked(),
        "value": value
      }

      self.save_current_data(data, index)
      dialog.close()

      
    btn_select.clicked.connect(select_file)
    btn_add_file.clicked.connect(add_file)
    btn_insert_file.clicked.connect(insert_file)
    btn_remove_file.clicked.connect(remove_file)
    btn_clear_file.clicked.connect(clear_file)
    files_field.selectionModel().selectionChanged.connect(file_selection_changed)
    file_type_field.currentIndexChanged.connect(file_type_changed)
    btn_save.clicked.connect(save_dialog)

    dialog.setLayout(layout)

    if not dataInfo is None:
      name_field.setText(dataInfo.get("name"))

      ft_type = dataInfo.get("type")
      if not ft_type is None:
        ft_type = DataType.get_item_by_value(ft_type)
        file_type_field.setCurrentText(ft_type.name)

      i_type = dataInfo.get("subtype")
      i_type = ImageType.get_item_by_value(i_type)
      if not i_type is None:
        type_field.setCurrentText(i_type.name)
      
      is_multiple = dataInfo.get("ismultiple")
      if is_multiple:
        multi_field.setChecked(True)
        value = dataInfo.get("value")
        if not value is None:
          if not isinstance(value, list):
            value = [value]
          files_field.addItems(value)
      else:
        multi_field.setChecked(False)
        value = dataInfo.get("value", "")
        selected_file.setText(value)

    dialog.exec()

  def build_scalar_dialog(self, dataInfo=None, index=None):
    dialog = QDialog(self)
    dialog.setMaximumWidth(700)
    layout = QVBoxLayout()

    name_layout = QHBoxLayout()
    name_label = QLabel("Variable Name", dialog)
    name_field = QLineEdit(dialog)
    name_layout.addWidget(name_label)
    name_layout.addWidget(name_field)
    layout.addLayout(name_layout)

    type_layout = QHBoxLayout()
    type_label = QLabel("Variable Type", dialog)
    type_field = QComboBox(dialog)
    type_layout.addWidget(type_label)
    type_layout.addWidget(type_field)
    layout.addLayout(type_layout)
    for i_type in ScalarType:
      type_field.addItem(i_type.name, userData=i_type)

    value_layout = QHBoxLayout()
    value_label = QLabel("Value", dialog)
    value_field = QLineEdit(dialog)
    value_field.setValidator(QIntValidator())
    value_field_dt = QDateTimeEdit(dialog)
    value_field_dt.setVisible(False)
    value_field_dt.setCalendarPopup(True)
    value_field_bool = QCheckBox(dialog)
    value_field_bool.setVisible(False)
    value_layout.addWidget(value_label)
    value_layout.addWidget(value_field)
    value_layout.addWidget(value_field_dt)
    value_layout.addWidget(value_field_bool)
    layout.addLayout(value_layout)
    layout.addStretch(1)

    btn_layout = QHBoxLayout()
    btn_save = QPushButton("Save", dialog)
    btn_cancel = QPushButton("Cancel", dialog)
  
    btn_layout.addStretch(1)
    btn_layout.addWidget(btn_cancel)
    btn_layout.addWidget(btn_save)
    layout.addLayout(btn_layout)

    def on_scalar_type_changed(idx):
      sel_type = type_field.currentText()
      value_field_dt.setVisible(ScalarType.DATETIME.name == sel_type)
      value_field_bool.setVisible(ScalarType.BOOL.name == sel_type)
      value_field.setVisible(ScalarType.DATETIME.name != sel_type and ScalarType.BOOL.name != sel_type)
      if sel_type == ScalarType.INT.name:
        value_field.setValidator(QIntValidator())
      elif sel_type == ScalarType.FLOAT.name:
        value_field.setValidator(QDoubleValidator())
      else:
        value_field.setValidator(None)
      
        
    def save_dialog():
      name = name_field.text()
      if name.strip() == "":
        self.show_error("variable name required!")
        return

      sel_type = type_field.currentText()
      value = value_field.text()

      if sel_type == ScalarType.INT.name:
        value = int(value)
      elif sel_type == ScalarType.FLOAT.name:
        value = float(value)
      elif sel_type == ScalarType.DATETIME.name:
        value = value_field_dt.text()
        value = value_field_dt.dateTimeFromText(value)
        value = value.toPyDateTime()
      elif sel_type == ScalarType.BOOL.name:
        value = value_field_bool.isChecked()

      data = {
        "name": name,
        "type": DataType.SCALAR.value,
        "subtype": type_field.currentData().value,
        "ismultiple": False,
        "value": value
      }

      self.save_current_data(data, index)
      dialog.close()

    btn_save.clicked.connect(save_dialog)
    btn_cancel.clicked.connect(dialog.close)
    type_field.currentIndexChanged.connect(on_scalar_type_changed)
    dialog.setLayout(layout)

    if not dataInfo is None:
      name_field.setText(dataInfo.get("name"))
      i_type = dataInfo.get("subtype")
      i_type = ScalarType.get_item_by_value(i_type)
      type_field.setCurrentText(i_type.name)
      value = dataInfo.get("value", "")

      if i_type == ScalarType.DATETIME:
        value_field_dt.setDateTime(value)
      elif i_type == ScalarType.BOOL:
        value_field_bool.setChecked(bool(value))
      else:
        value_field.setText(value)
        
    dialog.exec()


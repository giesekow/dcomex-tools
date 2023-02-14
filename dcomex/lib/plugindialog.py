import typing, copy
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QTableView, QDialog
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QComboBox
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTabWidget, QCheckBox
from PyQt5.QtCore import Qt, QStandardPaths
from .qtdata import TableModel
from .plugin_manager import PluginManager, PluginType, PluginGroupType

class PluginDialog(QDialog):
  def __init__(self, plugin_manager: PluginManager, parent: typing.Optional[QWidget] = None) -> None:
    super().__init__(parent)
    self._plugin_manager = plugin_manager
    self.setMinimumSize(700, 500)
    self.setWindowTitle("Plugin Configuration")
    self.setWindowModality(Qt.WindowModality.ApplicationModal)
    self.build_ui()

  def build_ui(self):
    self._layout = QVBoxLayout()
    self._tab = QTabWidget(self)
    
    self._plugins_page = QWidget(self)
    self._plugins_layout = QVBoxLayout()

    self._groups_page = QWidget(self)
    self._groups_layout = QVBoxLayout()

    self._tab.addTab(self._plugins_page, "Plugins")
    self._tab.addTab(self._groups_page, "Groups")

    self.build_plugins_table()
    self.build_plugins_buttons()
    self.build_groups_table()
    self.build_groups_buttons()

    self._plugins_page.setLayout(self._plugins_layout)
    self._groups_page.setLayout(self._groups_layout)

    self._layout.addWidget(self._tab)
    self.setLayout(self._layout)

  def build_plugins_table(self):
    items, headers = self.load_plugin_table_data()
    self.plugins_model = TableModel(items, headers, self)
    self.plugins_view = QTableView()
    self.plugins_view.setModel(self.plugins_model)
    self._plugins_layout.addWidget(self.plugins_view)

  def build_groups_table(self):
    items, headers = self.load_group_table_data()
    self.groups_model = TableModel(items, headers, self)
    self.groups_view = QTableView()
    self.groups_view.setModel(self.groups_model)
    self._groups_layout.addWidget(self.groups_view)

  def save_current_plugin_data(self, data, index=None):
    if index is None:
      self._plugin_manager.insert_plugin(data)
    else:
      self._plugin_manager.update_plugin(data, index)

    self.refresh_plugin_table()

  def save_current_group_data(self, data, index=None):
    if index is None:
      self._plugin_manager.insert_group(data)
    else:
      self._plugin_manager.update_group(data, index)

    self.refresh_group_table()

  def refresh_plugin_table(self):
    items, headers = self.load_plugin_table_data()
    self.plugins_model.deleteLater()
    self.plugins_model = TableModel(data=items, headers=headers, parent=self)
    self.plugins_view.setModel(self.plugins_model)

  def refresh_group_table(self):
    items, headers = self.load_group_table_data()
    self.groups_model.deleteLater()
    self.groups_model = TableModel(data=items, headers=headers, parent=self)
    self.groups_view.setModel(self.groups_model)

  def load_plugin_table_data(self):
    _data = self._plugin_manager.get_plugins()
    items = []
    for d in _data:
      i_type = d.get("type")
      if not i_type is None:
        i_type = PluginType.get_item_by_value(i_type)
        if not i_type is None:
          i_type = i_type.name

      items.append([d.get("name"), d.get("display"), i_type, d.get("group", ""), d.get("settings"), d.get("path"), d.doc_id])

    headers = ["Name", "Display", "Type", "Group", "Settings Path", "Data Path"]
    return items, headers

  def load_group_table_data(self):
    _data = self._plugin_manager.get_groups()
    items = []
    for d in _data:
      items.append([d.get("name"), d.get("display"), d.get("type"), d.doc_id])

    headers = ["Name", "Display", "Type"]
    return items, headers

  def build_plugins_buttons(self):
    widget = QWidget(self)
    layout = QHBoxLayout()

    btn_remove_selected = QPushButton("Remove Selected", widget)
    btn_remove_selected.clicked.connect(self.on_remove_selected_plugin_clicked)
    layout.addWidget(btn_remove_selected)

    btn_edit_selected = QPushButton("Edit Selected", widget)
    btn_edit_selected.clicked.connect(self.on_edit_selected_plugin_clicked)
    layout.addWidget(btn_edit_selected)

    btn_add = QPushButton("Add Plugin", widget)
    btn_add.clicked.connect(self.on_add_plugin_clicked)
    layout.addWidget(btn_add)

    layout.addStretch(1)

    btn_close = QPushButton("Close", widget)
    btn_close.clicked.connect(self.close)
    layout.addWidget(btn_close)

    widget.setLayout(layout)
    self._plugins_layout.addWidget(widget)

  def build_groups_buttons(self):
    widget = QWidget(self)
    layout = QHBoxLayout()

    btn_remove_selected = QPushButton("Remove Selected", widget)
    btn_remove_selected.clicked.connect(self.on_remove_selected_group_clicked)
    layout.addWidget(btn_remove_selected)

    btn_edit_selected = QPushButton("Edit Selected", widget)
    btn_edit_selected.clicked.connect(self.on_edit_selected_group_clicked)
    layout.addWidget(btn_edit_selected)

    btn_add = QPushButton("Add Group", widget)
    btn_add.clicked.connect(self.on_add_group_clicked)
    layout.addWidget(btn_add)

    layout.addStretch(1)

    btn_close = QPushButton("Close", widget)
    btn_close.clicked.connect(self.close)
    layout.addWidget(btn_close)

    widget.setLayout(layout)
    self._groups_layout.addWidget(widget)

  def on_add_plugin_clicked(self):
    self.build_plugin_dialog()

  def on_add_group_clicked(self):
    self.build_group_dialog()

  def on_remove_selected_plugin_clicked(self):
    result = QMessageBox.question(self, "Remove Plugin!", "Are you sure you want to remove plugin(s) ?",QMessageBox.Yes| QMessageBox.No)
    if result == QMessageBox.Yes:
      indexes = self.plugins_view.selectedIndexes()
      idxs = []
      for idx in indexes:
        idxs.append(idx.row())
      
      idxs = sorted(idxs, reverse=True)
      for idx in idxs:
        doc_id = self.plugins_model._data[idx][-1]
        self._plugin_manager.remove_plugin(doc_id)
      
      self.refresh_plugin_table()

  def on_remove_selected_group_clicked(self):
    result = QMessageBox.question(self, "Remove Plugin Group!", "Are you sure you want to remove plugin group(s) ?",QMessageBox.Yes| QMessageBox.No)
    if result == QMessageBox.Yes:
      indexes = self.groups_view.selectedIndexes()
      idxs = []
      for idx in indexes:
        idxs.append(idx.row())
      
      idxs = sorted(idxs, reverse=True)
      for idx in idxs:
        doc_id = self.groups_model._data[idx][-1]
        self._plugin_manager.remove_group(doc_id)
      
      self.refresh_group_table()

  def on_edit_selected_plugin_clicked(self):
    indexes = self.plugins_view.selectedIndexes()
    if len(indexes) > 0:
      index = indexes[0].row()
      doc_id = self.plugins_model._data[index][-1]
      data = self._plugin_manager.get_plugin(doc_id)
      index = doc_id
      if not isinstance(data, dict):
        return

      self.build_plugin_dialog(data, index)

  def on_edit_selected_group_clicked(self):
    indexes = self.groups_view.selectedIndexes()
    if len(indexes) > 0:
      index = indexes[0].row()
      doc_id = self.groups_model._data[index][-1]
      data = self._plugin_manager.get_group(doc_id)
      index = doc_id
      if not isinstance(data, dict):
        return

      self.build_group_dialog(data, index)

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

  def build_plugin_dialog(self, dataInfo=None, index=None):
    dialog = QDialog(self)
    dialog.setMaximumWidth(700)
    dialog.setMinimumWidth(500)
    layout = QVBoxLayout()

    name_layout = QHBoxLayout()
    name_label = QLabel("Plugin Name", dialog)
    name_field = QLineEdit(dialog)
    name_layout.addWidget(name_label)
    name_layout.addWidget(name_field)
    layout.addLayout(name_layout)

    dsp_name_layout = QHBoxLayout()
    dsp_name_label = QLabel("Display Name", dialog)
    dsp_name_field = QLineEdit(dialog)
    dsp_name_layout.addWidget(dsp_name_label)
    dsp_name_layout.addWidget(dsp_name_field)
    layout.addLayout(dsp_name_layout)

    type_layout = QHBoxLayout()
    type_label = QLabel("Type", dialog)
    type_field = QComboBox(dialog)
    type_layout.addWidget(type_label)
    type_layout.addWidget(type_field)
    layout.addLayout(type_layout)

    for i_type in PluginType:
      type_field.addItem(i_type.name, userData=i_type.value)

    group_layout = QHBoxLayout()
    group_label = QLabel("Plugin Group", dialog)
    group_field = QComboBox(dialog)
    group_layout.addWidget(group_label)
    group_layout.addWidget(group_field)
    layout.addLayout(group_layout)

    groups = self._plugin_manager.get_groups()
    for grp in groups:
      group_field.addItem(grp.get("name"), userData=grp.doc_id)

    btn_json_select = QPushButton("Select settings file", dialog)
    selected_json_file = QLabel("", dialog)
    layout.addWidget(btn_json_select)
    layout.addWidget(selected_json_file)

    btn_data_select = QPushButton("Select data path", dialog)
    selected_data_folder = QLabel("", dialog)
    layout.addWidget(btn_data_select)
    layout.addWidget(selected_data_folder)

    layout.addStretch(1)

    btn_layout = QHBoxLayout()
    btn_save = QPushButton("Save", dialog)
    btn_cancel = QPushButton("Cancel", dialog)
    btn_layout.addStretch(1)
    btn_layout.addWidget(btn_cancel)
    btn_layout.addWidget(btn_save)
    layout.addLayout(btn_layout)

    btn_cancel.clicked.connect(dialog.close)
    
    file_dialog = QFileDialog(dialog)
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    file_dialog.setNameFilter("JSON (*.json)")

    folder_dialog = QFileDialog(dialog)
    folder_dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)

    def select_json_file():
      if file_dialog.exec():
        filenames = file_dialog.selectedFiles()
        selected_json_file.setText(filenames[0])

    def select_data_folder():
      if folder_dialog.exec():
        filenames = folder_dialog.selectedFiles()
        selected_data_folder.setText(filenames[0])
        
    def save_dialog():
      name = name_field.text()
      display = dsp_name_field.text()
      json_path = selected_json_file.text()
      data_path = selected_data_folder.text()

      if name.strip() == "":
        self.show_error("Name required!")
        return

      if display.strip() == "":
        self.show_error("Display required!")
        return

      if json_path.strip() == "":
        self.show_error("JSON settings file required!")
        return

      data = {
        "name": name,
        "display": display,
        "path": data_path,
        "settings": json_path,
        "type": type_field.currentData(),
        "group": group_field.currentData(),
      }

      self.save_current_plugin_data(data, index)
      dialog.close()

    btn_json_select.clicked.connect(select_json_file)
    btn_data_select.clicked.connect(select_data_folder)
    btn_save.clicked.connect(save_dialog)

    dialog.setLayout(layout)

    if not dataInfo is None:
      name_field.setText(dataInfo.get("name"))
      dsp_name_field.setText(dataInfo.get("display"))
      selected_json_file.setText(dataInfo.get("settings", ""))
      selected_data_folder.setText(dataInfo.get("path", ""))

      ft_type = dataInfo.get("type")
      if not ft_type is None:
        ft_type = PluginType.get_item_by_value(ft_type)
        type_field.setCurrentText(ft_type.name)

      grp = dataInfo.get("group")
      if not grp is None:
        grp = self._plugin_manager.get_group(grp)
        if not grp is None:
          group_field.setCurrentText(grp.get("name"))

    dialog.exec()

  def build_group_dialog(self, dataInfo=None, index=None):
    dialog = QDialog(self)
    dialog.setMaximumWidth(700)
    dialog.setMinimumWidth(500)
    layout = QVBoxLayout()

    name_layout = QHBoxLayout()
    name_label = QLabel("Group Name", dialog)
    name_field = QLineEdit(dialog)
    name_layout.addWidget(name_label)
    name_layout.addWidget(name_field)
    layout.addLayout(name_layout)

    dsp_name_layout = QHBoxLayout()
    dsp_name_label = QLabel("Display Name", dialog)
    dsp_name_field = QLineEdit(dialog)
    dsp_name_layout.addWidget(dsp_name_label)
    dsp_name_layout.addWidget(dsp_name_field)
    layout.addLayout(dsp_name_layout)

    as_sub_menu_layout = QHBoxLayout()
    as_sub_menu_label = QLabel("Use as Sub Menu ?", dialog)
    as_sub_menu_field = QCheckBox(dialog)
    as_sub_menu_layout.addWidget(as_sub_menu_label)
    as_sub_menu_layout.addWidget(as_sub_menu_field)
    layout.addLayout(as_sub_menu_layout)

    type_layout = QHBoxLayout()
    type_label = QLabel("Type", dialog)
    type_field = QComboBox(dialog)
    type_layout.addWidget(type_label)
    type_layout.addWidget(type_field)
    layout.addLayout(type_layout)

    for i_type in PluginGroupType:
      type_field.addItem(i_type.name, userData=i_type.value)

    layout.addStretch(1)

    btn_layout = QHBoxLayout()
    btn_save = QPushButton("Save", dialog)
    btn_cancel = QPushButton("Cancel", dialog)
    btn_layout.addStretch(1)
    btn_layout.addWidget(btn_cancel)
    btn_layout.addWidget(btn_save)
    layout.addLayout(btn_layout)

    btn_cancel.clicked.connect(dialog.close)
        
    def save_dialog():
      name = name_field.text()
      display = dsp_name_field.text()
    
      if name.strip() == "":
        self.show_error("Name required!")
        return

      if display.strip() == "":
        self.show_error("Display required!")
        return

      data = {
        "name": name,
        "display": display,
        "submenu": as_sub_menu_field.isChecked(),
        "type": type_field.currentData()
      }

      self.save_current_group_data(data, index)
      dialog.close()

    btn_save.clicked.connect(save_dialog)

    dialog.setLayout(layout)

    if not dataInfo is None:
      name_field.setText(dataInfo.get("name"))
      dsp_name_field.setText(dataInfo.get("display"))
      as_sub_menu_field.setChecked(bool(dataInfo.get("submenu")))

      ft_type = dataInfo.get("type")
      if not ft_type is None:
        ft_type = PluginGroupType.get_item_by_value(ft_type)
        type_field.setCurrentText(ft_type.name)

    dialog.exec()
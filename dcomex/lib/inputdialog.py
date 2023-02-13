from datetime import datetime
import typing
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDialog, QGridLayout
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox
from PyQt5.QtWidgets import QMessageBox, QDateTimeEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from .data import DataType, ScalarType
from .workspace import Workspace

class InputDialog(QDialog):
  def __init__(self, workspace: Workspace, input_information: dict, has_outputs: bool = False, parent: typing.Optional[QWidget] = None) -> None:
    super().__init__(parent)
    self._workspace = workspace
    self._input_info = input_information
    self._input_data = {}
    self.output_prefix = ""
    self.has_output = has_outputs
    self.setMinimumSize(700, 500)
    self.setWindowTitle("Processing Input Information")
    self.setWindowModality(Qt.WindowModality.ApplicationModal)
    self.build_ui()

  def build_ui(self):
    self._layout = QVBoxLayout()
    self.prefix_field = None
    self.build_input_fields()
    self.build_buttons()
    self.setLayout(self._layout)

  def build_input_fields(self):
    self.fields = {}
    layout = QGridLayout()

    row = 0
    if self.has_output:
      prefix_label = QLabel("Output Prefix", self)
      self.prefix_field = QLineEdit(self)
      layout.addWidget(prefix_label, 0, 0)
      layout.addWidget(self.prefix_field, 0, 1)
      row = 1

    for k in self._input_info:
      data = self._input_info[k]
      label = QLabel(data.get("display"), self)
      layout.addWidget(label, row, 0)

      f_type = data.get("type")
      s_type = data.get("subtype")
      is_mult = data.get("ismultiple")
      is_required = data.get("required", False)

      if f_type != DataType.SCALAR.value:
        field = QComboBox(self)
        layout.addWidget(field, row, 1)
        options = self._workspace.get_data_type(f_type, s_type, is_mult)
        if not is_required:
          field.addItem("[N/A]", userData={"value": None})

        for opt in options:
          field.addItem(opt.get("name"), userData=opt)
      
        self.fields[k] = field
      else:
        if s_type == ScalarType.DATETIME.value:
          field = QDateTimeEdit(self)
          field.setCalendarPopup(True)
          if "default" in data:
            df = data.get("default")
            if not df is None:
              val = datetime.fromtimestamp(df)
              field.setDateTime(val)

        elif s_type == ScalarType.BOOL.value:
          field = QCheckBox(self)
        else:
          field = QLineEdit(self)
          if s_type == ScalarType.INT.value:
            field.setValidator(QIntValidator())
          elif s_type == ScalarType.FLOAT.value:
            field.setValidator(QDoubleValidator())

          if "default" in data:
            field.setText(str(data.get("default")))

        layout.addWidget(field, row, 1)
        self.fields[k] = field

        

      row += 1

    self._layout.addLayout(layout)
    self._layout.addStretch(1)

  def build_buttons(self):
    widget = QWidget(self)
    layout = QHBoxLayout()

    layout.addStretch(1)

    btn_close = QPushButton("Cancel", widget)
    btn_close.clicked.connect(self.close)
    layout.addWidget(btn_close)

    btn_process = QPushButton("Process", widget)
    btn_process.clicked.connect(self.save_data)
    layout.addWidget(btn_process)

    widget.setLayout(layout)
    self._layout.addWidget(widget)

  def save_data(self):
    input_data = {}

    for k in self._input_info:
      field = self.fields.get(k)
      i_data = self._input_info[k]
      f_type = i_data.get("type")
      s_type = i_data.get("subtype")
      required = i_data.get("required")
      df = i_data.get("default")

      if not field is None:
        if not f_type == DataType.SCALAR.value:
          dt = field.currentData()
          if not dt is None:
            input_data[k] = dt.get("value")
        else:
          if s_type == ScalarType.DATETIME.value:
            input_data[k] = field.dateTime().toPyDateTime().timestamp()
          elif s_type == ScalarType.BOOL.value:
            input_data[k] = field.isChecked()
          else:
            txt = field.text()
            if txt.strip() != "":
              if s_type == ScalarType.INT.value:
                input_data[k] = int(txt)
              elif s_type == ScalarType.FLOAT.value:
                input_data[k] = float(txt)
              else:
                input_data[k] = txt
        
      if not k in input_data:
        if not df is None:
          input_data[k] = df
        elif required:
          self.show_error(f"{i_data.get('display')} is required!")
          return

    self._input_data = input_data
    if not self.prefix_field is None:
      self.output_prefix = self.prefix_field.text().strip()
    else:
      self.output_prefix = ""

    return self.accept()

  def get_last_input_data(self) -> dict:
    return self._input_data

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

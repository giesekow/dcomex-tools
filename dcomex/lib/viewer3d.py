from datetime import datetime
import numpy as np
import nibabel as nb
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDialog, QGridLayout
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox
from PyQt5.QtWidgets import QMessageBox, QDateTimeEdit
from PyQt5.QtCore import Qt
from .viewer import ViewPanel, View3DPanel
from .inputdialog import InputDialog
from .misc import QHLine

class Viewer3D(QWidget):
  def __init__(self, workspace, parent=None) -> None:
    super().__init__(parent)
    self.images = []
    self.zooms = []
    self.point = [0, 0, 0]
    self.image_index = -1
    self.bgcolor = "#ffd167"
    self.scale = 1
    self.workspace = workspace
    self.range = []
    self.seg_image = None
    self.build_ui()

  def build_ui(self):
    self.main_layout = QHBoxLayout()
    self.setLayout(self.main_layout)
    self.build_viewer()
    self.build_side_panel()

  def build_side_panel(self):
    self.side_panel = QWidget(self)
    self.side_panel.setMinimumWidth(200)
    self.side_panel.setMaximumWidth(200)
    self.side_layout = QVBoxLayout()

    btn_load_img = QPushButton('Load Image', self)
    btn_load_img.clicked.connect(self.on_load_raw_image)

    btn_load_seg = QPushButton('Load Segmentation', self)
    btn_load_seg.clicked.connect(self.on_load_seg_image)

    self.side_layout.addWidget(btn_load_img)
    self.side_layout.addWidget(btn_load_seg)

    i_info_title = QLabel('Information')
    self.side_layout.addWidget(i_info_title, alignment=Qt.AlignCenter)
    self.side_layout.addWidget(QHLine())

    info_layout = QGridLayout()

    i_cord_label = QLabel('Coord(x,y,z): ', self)
    self.i_cord_value = QLabel('(0,0,0)', self)
    info_layout.addWidget(i_cord_label, 0, 0, alignment=Qt.AlignRight)
    info_layout.addWidget(self.i_cord_value, 0, 1)

    i_intensity_label = QLabel('Intensity: ', self)
    self.i_intensity_value = QLabel('N/A', self)
    info_layout.addWidget(i_intensity_label, 1, 0, alignment=Qt.AlignRight)
    info_layout.addWidget(self.i_intensity_value, 1, 1)


    self.side_layout.addLayout(info_layout)
    self.side_layout.addStretch(1)
    self.side_panel.setLayout(self.side_layout)
    self.main_layout.addWidget(self.side_panel)

  def update_side_panel(self):
    pt = self.point
    self.i_cord_value.setText(f"({pt[0]},{pt[1]},{pt[2]})")
    self.i_intensity_value.setText(f"{self.images[self.image_index][pt[0], pt[1], pt[2]]}")

  def on_load_raw_image(self):
    dialog = InputDialog(self.workspace, {"raw_input": {"type": "image", "subtype": "nifti", "display": "Select data"}}, False, self)
    if dialog.exec():
      data = dialog.get_last_input_data()
      if "raw_input" in data:
        filename = data.get("raw_input")
        self.load_image(filename)
        self.update_image_2d_points(reset=True)

  def on_load_seg_image(self):
    dialog = InputDialog(self.workspace, {"raw_input": {"type": "image", "subtype": "nifti", "display": "Select data"}}, False, self)
    if dialog.exec():
      data = dialog.get_last_input_data()
      if "raw_input" in data:
        filename = data.get("raw_input")
        self.load_image(filename, is_seg=True)
        self.update_image_3d_points(reset=True)

  def build_viewer(self):
    self.viewer_panel = QWidget(self)
    self.viewer_layout = QGridLayout()
    self.viewer_panel.setLayout(self.viewer_layout)
    self.viewer_layout.setSpacing(5)

    self.top_left_panel = ViewPanel(self)
    self.top_right_panel = ViewPanel(self)
    self.bottom_left_panel = View3DPanel(self)
    self.bottom_right_panel = ViewPanel(self)

    self.top_left_panel.sliderValueChanged.connect(self.on_slider_value_changed(2))
    self.bottom_right_panel.sliderValueChanged.connect(self.on_slider_value_changed(1))
    self.top_right_panel.sliderValueChanged.connect(self.on_slider_value_changed(0))

    self.top_left_panel.pointChanged.connect(self.on_point_changed(2))
    self.bottom_right_panel.pointChanged.connect(self.on_point_changed(1))
    self.top_right_panel.pointChanged.connect(self.on_point_changed(0))

    self.top_left_panel.set_point_color((0, 0, 255, 128))
    self.bottom_right_panel.set_point_color((0, 255, 0, 128))
    self.top_right_panel.set_point_color((255, 0, 0, 128))

    self.viewer_layout.addWidget(self.top_left_panel, 1, 1)
    self.viewer_layout.addWidget(self.top_right_panel, 1, 2)
    self.viewer_layout.addWidget(self.bottom_left_panel, 2, 1)
    self.viewer_layout.addWidget(self.bottom_right_panel, 2, 2)

    self.main_layout.addWidget(self.viewer_panel, stretch=1)

  def on_slider_value_changed(self, index):
    def handler(value):
      self.point[index] = value
      self.update_image_2d_points()
      self.update_image_3d_points()

    return handler

  def on_point_changed(self, index):
    def handler(value):
      pt = [int(p) for p in value]
      pt.insert(index, self.point[index])
      self.point = pt
      self.update_image_2d_points()
      self.update_image_3d_points()

    return handler

  def load_image(self, filename, is_seg=False):
    img = nb.load(filename)
    img = nb.as_closest_canonical(img)
    hdr = img.get_header()
    zooms = hdr.get_zooms()
    data = img.get_fdata()
    
    data = np.flip(data)

    if not is_seg:
      self.range.append([data.min(), data.max()])
      self.images.append(data)
      self.zooms.append(zooms)
      self.point = [0, 0, 0]
      self.image_index += 1
    else:
      self.seg_image = data

  def update_image_2d_points(self, reset=False):
    index, point = (self.image_index, self.point)
    img = self.images[index]
    rng = self.range[index]
    zoom = self.zooms[index]
    sh = img.shape

    # Prepare and show tl
    self.top_left_panel.set_image(img[:, :, point[2]], sh[2], point[2], rng)
    self.bottom_right_panel.set_image(img[:, point[1], :], sh[1], point[1], rng)
    self.top_right_panel.set_image(img[point[0], :, :], sh[0], point[0], rng)
    
    # Set cursor point
    self.top_left_panel.set_point([point[0], point[1]])
    self.bottom_right_panel.set_point([point[0], point[2]])
    self.top_right_panel.set_point([point[1], point[2]])

    self.top_left_panel.set_zoom([zoom[0], zoom[1]])
    self.bottom_right_panel.set_zoom([zoom[0], zoom[2]])
    self.top_right_panel.set_zoom([zoom[1], zoom[2]])

    self.top_left_panel.update_ui(reset=reset)
    self.top_right_panel.update_ui(reset=reset)
    self.bottom_right_panel.update_ui(reset=reset)
    self.update_side_panel()

  def update_image_3d_points(self, reset=False):
    index, point = (self.image_index, self.point)
    zoom = self.zooms[index]
    
    if not self.seg_image is None:
      self.bottom_left_panel.set_image(self.seg_image)
      self.bottom_left_panel.set_point(point)
      self.bottom_left_panel.set_zoom(zoom)
      self.bottom_left_panel.update_ui(reset=reset)
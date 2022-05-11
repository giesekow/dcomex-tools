from cmath import rect
from venv import create
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtWidgets import QScrollBar
from PyQt5.QtCore import Qt, pyqtSignal, QPointF
from PyQt5.QtGui import QImage, QPixmap
from pyqtgraph.opengl import GLVolumeItem, GLViewWidget, GLLinePlotItem
import pyqtgraph as pg

class ImageView(pg.ImageView):
  onWheelEvent = pyqtSignal(int)
  pointChanged = pyqtSignal(list)
  def __init__(self, parent=None):
    super().__init__(parent)
    self.has_image = False
    self.view = self.getView()
    self.view.wheelEvent = self.wheelEvent
    self.view.mouseClickEvent = self._mouseClickEvent
    self.current_point = [0, 0]
    self.point_color = None
    self.current_zoom = [1, 1]
    self.h_line_item = None
    self.v_line_item = None
    self.ui.histogram.hide()
    self.ui.roiBtn.hide()
    self.ui.menuBtn.hide()

  def set_image(self, img, reset=False):
    if self.has_image and (not reset):
      _state = self.getView().getState()
      self.getImageItem().setImage(img, autoLevels=False, scale=self.current_zoom)
      self.plot_current_point()
      self.getView().setState(_state)
    else:
      self.setImage(img, autoLevels=False, scale=self.current_zoom)
      self.plot_current_point()

    self.has_image = True

  def set_point(self, pt):
    self.current_point = pt

  def set_zoom(self, zoom):
    self.current_zoom = zoom

  def set_point_color(self, color):
    self.point_color = color

  def plot_current_point(self):
    pt = QPointF(self.current_point[0] * self.current_zoom[0], self.current_point[1] * self.current_zoom[1])
    if self.v_line_item is None:
      self.v_line_item = pg.InfiniteLine(pt.x() + 0.5, angle=90, pen=self.point_color)
      self.view.addItem(self.v_line_item)
    else:
      self.v_line_item.setValue(pt.x() + 0.5)

    if self.h_line_item is None:
      self.h_line_item = pg.InfiniteLine(pt.y() + 0.5, angle=0, pen=self.point_color)
      self.view.addItem(self.h_line_item)
    else:
      self.h_line_item.setValue(pt.y() + 0.5)
      
  def wheelEvent(self, event):
    event.accept()
    delta = event.delta()
    notches = delta // 120
    self.onWheelEvent.emit(notches)

  def _mouseClickEvent(self, event):
    if event.button() == 1 and self.has_image:
      zm = self.current_zoom
      spt = self.view.mapSceneToView(event.pos())
      spt = QPointF(max(0, int(spt.x() / zm[0])), max(0, int(spt.y() / zm[1])))
      for v in self.view.addedItems:
        if isinstance(v, pg.ImageItem):
          spt = QPointF(min(spt.x(), v.width()-1), min(spt.y(), v.height()-1))

      if self.current_point[0] != spt.x() or self.current_point[1] != spt.y():
        self.current_point = [spt.x(), spt.y()]
        self.plot_current_point()
        self.pointChanged.emit(self.current_point)

class ViewPanel(QWidget):
  sliderValueChanged = pyqtSignal(int)
  pointChanged = pyqtSignal(list)
  
  def __init__(self, parent=None) -> None:
    super().__init__(parent)
    self.image = None
    self.range = None
    self.bgcolor = "#7a7976"
    self.scale = 2
    self.ignore_changes = False
    self.build_ui()

  def build_ui(self):
    self.main_layout = QVBoxLayout()
    self.main_label = ImageView(self)
    self.main_label.onWheelEvent.connect(self.on_wheel_event)
    self.main_label.pointChanged.connect(self.pointChanged)
    self.main_label.getView().setBackgroundColor('gray')
    
    b_layout = QHBoxLayout()
    
    self.scroll_bar = QScrollBar(Qt.Horizontal, self)
    self.scroll_bar.setMaximum(100)
    self.scroll_bar.valueChanged.connect(self.on_slider_value_changed)
    self.scroll_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    
    self.scroll_text = QLabel(self)
    self.scroll_text.setMinimumWidth(50)
    self.scroll_text.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
    
    b_layout.addWidget(self.scroll_text)
    b_layout.addWidget(self.scroll_bar)

    self.main_layout.addWidget(self.main_label)
    self.main_layout.addLayout(b_layout)
    self.setLayout(self.main_layout)

  def set_image(self, image, slices=1, index=1, rng=None):
    self.ignore_changes = True
    self.image = image
    self.range = rng
    self.scroll_bar.setMaximum(slices-1)
    self.scroll_bar.setValue(index)
    self.scroll_text.setText(f"{index + 1}/{slices}")
    self.ignore_changes = False

  def set_point(self, point):
    self.main_label.set_point(point)
  
  def set_point_color(self, color):
    self.main_label.set_point_color(color)

  def set_zoom(self, zoom):
    self.main_label.set_zoom(zoom)

  def update_ui(self, reset=False):
    if not self.image is None:
      img = self.image
      self.main_label.set_image(self.create_image(img), reset=reset)
  
  def on_slider_value_changed(self):
    if not self.ignore_changes:
      self.sliderValueChanged.emit(self.scroll_bar.value())

  def resizeEvent(self, event):
    super().resizeEvent(event)
    self.update_ui()

  def wheelEvent(self, event) -> None:
    super().wheelEvent(event)
    notches = event.angleDelta().y() // 120
    v = self.scroll_bar.value()
    v -= notches
    if v >= 0 and v <= self.scroll_bar.maximum():
      self.scroll_bar.setValue(v)

  def on_wheel_event(self, value):
    if not self.image is None:
      v = self.scroll_bar.value()
      v -= value
      if v >= 0 and v <= self.scroll_bar.maximum():
        self.scroll_bar.setValue(v)

  def create_image(self, img_data, is_rgb=False):
    if not is_rgb:  
      img = np.zeros(img_data.shape + (3, ))
      img[:, :, 0] = img_data
      img[:, :, 1] = img_data
      img[:, :, 2] = img_data
      img_data = img

    if not self.range is None:
      mi, ma = self.range
    else:
      ma = img_data.max()
      mi = img_data.min()

    if ma - mi != 0:
      img_data = ((img_data - mi) * 1.0) / (ma - mi)
    elif ma != 0:
      img_data = (img_data * 1.0) / ma

    return img_data

class View3DPanel(QWidget):
  sliderValueChanged = pyqtSignal(int)
  
  def __init__(self, parent=None) -> None:
    super().__init__(parent)
    self.image = None
    self.point = (0, 0, 0)
    self.shape = (0, 0, 0)
    self.bgcolor = "#7a7976"
    self.zoom = (1, 1, 1)
    self.scale = 1
    self.colors = {
      '0': [0, 0, 0, 0],
      '1': [255, 0, 0, 255],
      '2': [0, 255, 0, 255],
      '3': [0, 0, 255, 255],
    }
    self.ignore_changes = False
    self.view_item = None
    self.x_view_line = None
    self.y_view_line = None
    self.z_view_line = None
    self.build_ui()

  def build_ui(self):
    self.main_layout = QVBoxLayout()
    
    self.viewer = GLViewWidget(self)
    self.viewer.setCameraPosition(distance=1000)

    self.main_layout.addWidget(self.viewer)
    self.setLayout(self.main_layout)

  def set_image(self, image):
    self.ignore_changes = True
    self.image = np.flip(image, axis=2)
    self.shape = image.shape
    self.ignore_changes = False

  def set_point(self, point):
    self.point = point

  def set_zoom(self, zoom):
    #self.zoom = zoom
    pass

  def update_ui(self, reset=False):
    if not self.image is None:
      self.draw_cursor_lines()

      if self.view_item is None:
        img = self.image
        img = self.create_image(img)
        self.view_item = GLVolumeItem(img, sliceDensity=self.scale, smooth=True, glOptions='translucent')
        self.viewer.addItem(self.view_item)
      elif reset:
        img = self.image
        img = self.create_image(img)
        self.view_item.setData(img)

  def draw_cursor_lines(self):
    zm = self.zoom
    pt = [p for p in self.point]
    pt[2] = self.shape[2] - pt[2] - 1
    pt = [p*z for p,z in zip(pt, zm)]
    sh = [s*z for s,z in zip(self.shape, zm)]

    x_points = np.array([[0, pt[1], pt[2]],[sh[0], pt[1], pt[2]]])
    y_points = np.array([[pt[0], 0, pt[2]],[pt[0], sh[1], pt[2]]])
    z_points = np.array([[pt[0], pt[1], 0],[pt[0], pt[1], sh[2]]])

    if self.x_view_line is None:
      self.x_view_line = GLLinePlotItem(color=(1, 0, 0, 1), antialias=True, mode='lines')
      self.viewer.addItem(self.x_view_line)

    if self.y_view_line is None:
      self.y_view_line = GLLinePlotItem(color=(0, 1, 0, 1), antialias=True, mode='lines')
      self.viewer.addItem(self.y_view_line)

    if self.z_view_line is None:
      self.z_view_line = GLLinePlotItem(color=(0, 0, 1, 1), antialias=True, mode='lines')
      self.viewer.addItem(self.z_view_line)

    self.x_view_line.setData(pos=x_points)
    self.y_view_line.setData(pos=y_points)
    self.z_view_line.setData(pos=z_points)
  
  def on_slider_value_changed(self):
    pass

  def resizeEvent(self, event):
    super().resizeEvent(event)
    #self.update_ui()

  def wheelEvent(self, event) -> None:
    super().wheelEvent(event)

  def create_image(self, img_data, is_rgb=False):
    if not is_rgb: 
      img = np.empty(img_data.shape + (4, ), dtype=np.ubyte)
      for k in self.colors:
        if k == '0':
          continue
        ind = np.where(img_data == int(k))
        img[ind] = self.colors[k]
      
      img_data = img

    return img_data
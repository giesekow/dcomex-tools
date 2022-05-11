import typing
from PyQt5.QtWidgets import QWidget, QMainWindow, QAction, QDockWidget, QFileDialog, QVBoxLayout
from PyQt5.QtWidgets import QMenuBar, QMessageBox, QProgressBar, QStatusBar, QLabel, QTabWidget
from PyQt5.QtCore import Qt
from .workspace import Workspace
from .datadialog import DataDialog
from .inputdialog import InputDialog
from .plugindialog import PluginDialog
from .plugin_manager import PluginGroupType, PluginManager
from .qtplugin import QtPlugin as Plugin
from .viewer3d import Viewer3D

class MainWindow(QMainWindow):
  def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
    super().__init__(parent)
    self.windows = []
    self._current_workspace = Workspace()
    self._plugin_manager = PluginManager()
    self._current_plugins = []
    self.build_ui()
    self.on_3d_view_open()

  def build_ui(self):
    self.setMinimumSize(700, 700)
    self.build_central_page()
    self.build_menu()
    self.build_status_bar()

  def build_central_page(self):
    self.tabs = QTabWidget(self)
    self.tabs.setTabsClosable(True)
    self.tabs.tabCloseRequested.connect(self.on_tab_close)
    self.setCentralWidget(self.tabs)

  def on_tab_close(self, index):
    result = QMessageBox.question(self, "Close Viewer!", "Are you sure you want to close viewer ?", QMessageBox.Yes| QMessageBox.No)
    if result == QMessageBox.Yes:
      if index < self.tabs.count():
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        widget.deleteLater()

  def build_menu(self):
    menuBar = self.menuBar()
    self.build_file_menu(menuBar)

    m_data = menuBar.addAction("&Data")
    m_data.triggered.connect(self.show_data_dialog)

    m_plugin = menuBar.addAction("Plu&gins")
    m_plugin.triggered.connect(self.show_plugin_dialog)

    #m_pipeline = menuBar.addAction("Pipe&lines")
    #m_pipeline.triggered.connect(self.show_pipeline_dialog)

    self.m_process = None
    self.m_view = None
    self.m_window = None

    self.build_view_menu(menuBar)
    self.build_process_menu(menuBar)
    # self.build_window_menu(menuBar)

  def build_status_bar(self):
    statusBar = QStatusBar(self)
    statusBar.setSizeGripEnabled(False)
    self.pbar = QProgressBar(self)
    self.pbar_text = QLabel("", self)
    statusBar.addPermanentWidget(self.pbar, 1)
    statusBar.addPermanentWidget(self.pbar_text)
    self.pbar.setVisible(False)
    self.pbar_text.setVisible(False)
    self.setStatusBar(statusBar)

  def build_file_menu(self, menuBar: QMenuBar):
    m_file = menuBar.addMenu("&File")

    m_new = QAction("&New", self)
    m_new.triggered.connect(self.new_workspace_file)
    m_file.addAction(m_new)

    m_open = QAction("&Open", self)
    m_open.triggered.connect(self.open_workspace_file)
    m_file.addAction(m_open)

    m_save = QAction("&Save", self)
    m_save.triggered.connect(self.save_workspace_file)
    m_file.addAction(m_save)

    m_file.addSeparator()

    m_exit = QAction("E&xit", self)
    m_exit.triggered.connect(self.close)
    m_file.addAction(m_exit)

  def build_process_menu(self, menuBar: QMenuBar):
    if self.m_process is None:
      self.m_process = menuBar.addMenu("&Process")

    self.m_process.clear()
    p_grps = self._plugin_manager.find_group_by_type(PluginGroupType.PROCESSING.value)
    p_grps = [{"is_none": True}] + p_grps
    for grp in p_grps:
      sm = self.m_process
      if bool(grp.get("submenu")):
        sm = self.m_process.addMenu(grp.get("display"))
      
      pms = self._plugin_manager.find_plugin_by_group(None) if "is_none" in grp else self._plugin_manager.find_plugin_by_group(grp.doc_id)

      for d in pms:
        act = QAction(d.get("display"), self)
        act.triggered.connect(self.on_process_clicked(d.doc_id))
        sm.addAction(act)
  
  def build_view_menu(self, menuBar: QMenuBar):
    if self.m_view is None:
      self.m_view = menuBar.addMenu("&Viewer")

    self.m_view.clear()
    act_vw_3d_nifti = QAction('Volume 3D', self)
    self.m_view.addAction(act_vw_3d_nifti)
    act_vw_3d_nifti.triggered.connect(self.on_3d_view_open)

    self.m_view.addSeparator()

    p_grps = self._plugin_manager.find_group_by_type(PluginGroupType.VIEWER.value)
    p_grps = [{"is_none": True}] + p_grps

    for grp in p_grps:
      sm = self.m_view
      if bool(grp.get("submenu")):
        sm = self.m_view.addMenu(grp.get("display"))
      
      pms = self._plugin_manager.find_plugin_by_group(None) if "is_none" in grp else self._plugin_manager.find_plugin_by_group(grp.doc_id)

      for d in pms:
        if d.get("group") is None and (d.get("viewer") is None or d.get("viewer") == False):
          continue

        act = QAction(d.get("display"), self)
        act.triggered.connect(self.on_process_clicked(d.doc_id))
        sm.addAction(act)

  def on_3d_view_open(self):
    cnt = self.tabs.count() + 1
    self.build_3d_viewer(f"Volume 3D {cnt}")

  def build_window_menu(self, menuBar: QMenuBar):
    m_windows = menuBar.addMenu("&Windows")

  def new_workspace_file():
    pass

  def open_workspace_file(self):
    filename, filt = QFileDialog.getOpenFileName(self, caption="Open Workspace", filter="JSON (*.json)")
    if filename == "":
      return

    self._current_workspace.load(filename)

  def save_workspace_file(self):
    filename, filt = QFileDialog.getSaveFileName(self, caption="Save Workspace", filter="JSON (*.json)")
    if filename == "":
      return

    if not filename.lower().endswith(".json"):
      filename = filename + ".json"

    self._current_workspace.save(filename)

  def build_3d_viewer(self, name: str):
    self.viewer_3d = Viewer3D(self._current_workspace, self)
    self.tabs.addTab(self.viewer_3d, name)

  def build_2d_viewer(self):
    pass

  def build_mesh_viewer(self):
    pass

  def show_data_dialog(self):
    d = DataDialog(workspace=self._current_workspace)
    d.exec()

  def show_plugin_dialog(self):
    d = PluginDialog(plugin_manager=self._plugin_manager)
    d.exec()
    self.build_process_menu(self.menuBar())
    self.build_view_menu(self.menuBar())

  def show_pipeline_dialog(self):
    pass
    
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

  def update_progress_bar(self):
    if len(self._current_plugins) > 0:
      self.pbar.setRange(0, 0)
      self.pbar_text.setText(f"Processing {len(self._current_plugins)} job(s)")
      self.pbar.setVisible(True)
      self.pbar_text.setVisible(True)
    else:
      self.pbar.setMaximum(100)
      self.pbar_text.setText("")
      self.pbar.setVisible(False)
      self.pbar_text.setVisible(False)


  # Plugin Processing
  def on_process_clicked(self, process_id):
    def handler():
      data = self._plugin_manager.get_plugin(process_id)
      p = Plugin(data, self._plugin_manager)
      
      p.finished.connect(self.on_plugin_finished(p))
      p.completed.connect(self.on_plugin_completed)
      p.errored.connect(self.on_plugin_error)

      if p.has_inputs() or p.has_outputs():
        req_inputs = p.input_information()
        dialog = InputDialog(self._current_workspace, req_inputs, p.has_outputs(), self)
        if dialog.exec():
          p.set_inputs(dialog.get_last_input_data(), dialog.output_prefix)
          self._current_plugins.append(p)
          self.update_progress_bar()
          p.run()
      else:
        self._current_plugins.append(p)
        self.update_progress_bar()
        p.run()

    return handler

  def on_plugin_completed(self, data):
    for k in data:
      output = data[k]
      output["name"] = k
      self._current_workspace.data.append(output)
    
    self._current_workspace.save()
    self.show_msg("Processing completed!")

  def on_plugin_error(self, err):
    self.show_error(err)

  def on_plugin_finished(self, plugin: Plugin):
    def handler():
      self._current_plugins.remove(plugin)
      plugin.deleteLater()
      self.update_progress_bar()

    return handler

  def closeEvent(self, event):
    result = QMessageBox.question(self, "Confirm Exit", "Are you sure you want to exit ?", QMessageBox.Yes| QMessageBox.No)
    event.ignore()

    if result == QMessageBox.Yes:
      for p in self._current_plugins:
        p.terminate()

      event.accept()

  
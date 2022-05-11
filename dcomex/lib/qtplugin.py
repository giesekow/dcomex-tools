import subprocess, json
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess, sys, json, tempfile
from .utils import executionCode
from .plugin import Plugin

class QtWorker(QThread):
  
  completed = pyqtSignal(dict)

  def __init__(self, function_name, executable=None, args=[], kwargs={}, modulePaths=[]):
    QThread.__init__(self)
    self.function_name=function_name
    self.executable=executable
    self.args=args
    self.kwargs=kwargs
    self.modulePaths=modulePaths
    self.output=None
    self.done=False

  def run(self):
    function_name=self.function_name
    executable=self.executable
    args=self.args
    kwargs=self.kwargs
    modulePaths=self.modulePaths

    if executable is None:
      executable = sys.executable

    if modulePaths is None:
      modulePaths = []

    with tempfile.NamedTemporaryFile(delete=True, suffix=".json") as tmp_file:
      data = {"function_name": function_name, "args": args, "kwargs": kwargs, "modules": modulePaths, "output": tmp_file.name}
      subprocess.run([executable, "-c", executionCode], input=str.encode(json.dumps(data)))
      output = json.load(tmp_file)
      self.output = output
      self.done = True

      self.completed.emit(self.output)
    
  def get_output(self):
    return self.output

class QtPlugin(QtCore.QObject, Plugin):
  completed = QtCore.pyqtSignal(dict)
  errored = QtCore.pyqtSignal(str)
  finished = QtCore.pyqtSignal()

  def __init__(self, data, manager, parent=None, **kwargs) -> None:
    QtCore.QObject.__init__(self, parent=parent)
    Plugin.__init__(self, data=data, manager=manager, kwargs=kwargs)

  def on_error(self, error): # to be handled by inhered class
    self.last_error = error
    self.errored.emit(error)

  def on_completed(self, output): # to be handled by inhered class
    self.last_output = output
    self.completed.emit(output)

  def on_finished(self): # to be handled by inhered class
    self.finished.emit()

  def on_python_run(self, function_name, executable, modules, args, kwargs): # to be handled by inhered class and call _process_completed when done
    if not self.worker is None:
      self.worker.deleteLater()

    self.worker = QtWorker(function_name=function_name, executable=executable, modulePaths=modules, args=[], kwargs=kwargs)
    self.worker.completed.connect(self._process_completed)
    self.worker.start()
  
  def on_executable_run(self, command):
    subprocess.Popen(command)
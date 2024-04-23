import subprocess, threading, sys, json, tempfile, os

from numpy import searchsorted
from .utils import executionCode
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QRunnable

_thread = QThread()

class Worker(threading.Thread):
  def __init__(self, function_name, executable=None, args=[], kwargs={}, modulePaths=[], callback=None):
    threading.Thread.__init__(self)
    self.function_name=function_name
    self.executable=executable
    self.args=args
    self.kwargs=kwargs
    self.modulePaths=modulePaths
    self.output=None
    self.done=False
    self.callback = callback

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

    with tempfile.TemporaryDirectory() as tmp_dir:
      tmp_file_name = os.path.join(tmp_dir, "job_results.json")
      data = {"function_name": function_name, "args": args, "kwargs": kwargs, "modules": modulePaths, "output": tmp_file_name}
      subprocess.run([executable, "-c", executionCode], input=str.encode(json.dumps(data)))

      if os.path.exists(tmp_file_name):
        with open(tmp_file_name, 'r') as tmp_file:
          self.output = json.load(tmp_file)
      else:
        self.output = {}

      self.done = True

      if self.callback:
        self.callback(self.output)
  
  def get_output(self):
    return self.output

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

    with tempfile.TemporaryDirectory() as tmp_dir:
      tmp_file_name = os.path.join(tmp_dir, "job_results.json")
      data = {"function_name": function_name, "args": args, "kwargs": kwargs, "modules": modulePaths, "output": tmp_file_name}
      subprocess.run([executable, "-c", executionCode], input=str.encode(json.dumps(data)))
      
      if os.path.exists(tmp_file_name):
        with open(tmp_file_name, 'r') as tmp_file:
          self.output = json.load(tmp_file)
      else:
        self.output = {}

      self.done = True

      self.completed.emit(self.output)
    
  def get_output(self):
    return self.output

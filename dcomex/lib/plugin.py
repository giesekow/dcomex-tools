from datetime import datetime
import os, subprocess, json, pathlib, threading, sys, tempfile
from .data import DataType, ScalarType
from .utils import executionCode
from .plugin_manager import PluginType

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

    with tempfile.NamedTemporaryFile(delete=True, suffix=".json") as tmp_file:
      data = {"function_name": function_name, "args": args, "kwargs": kwargs, "modules": modulePaths, "output": tmp_file.name}
      subprocess.run([executable, "-c", executionCode], input=str.encode(json.dumps(data)))
      output = json.load(tmp_file)
      self.output = output
      self.done = True

      if self.callback:
        self.callback(self.output)
  
  def get_output(self):
    return self.output

  def deleteLater(self):
    pass

class Plugin:
  def __init__(self, data=None, manager=None, **kwargs) -> None:
    self._data = data
    self._manager = manager
    self.kwargs = kwargs
    self.settings = {}
    self.worker = None
    self.output_prefix = ""
    self.input_data = {}
    self.last_error = None
    self.last_output = None
    self._load_info()

  def _load_info(self):
    try:
      if "settings" in self._data:
        filename = self._data.get("settings")
        with open(filename, "r") as json_file:
          d = json.load(json_file)
          if self.check_settings_data(d):
            self.settings = d
            return True
          else:
            return "Error in settings file"
      else:
        return "No settings file specified"
    except Exception as ex:
      return str(ex)

  def check_settings_data(self, data):
    return True

  def set_inputs(self, data: dict, output_prefix: str = "") -> None:
    self.input_data = data
    self.output_prefix = output_prefix

  def has_inputs(self):
    if "inputs" in self.settings:
      inputs = self.settings.get("inputs")
      if not inputs is None:
        if isinstance(inputs, dict):
          return len(inputs.keys()) > 0

    return False

  def has_outputs(self):
    if "outputs" in self.settings:
      outputs = self.settings.get("outputs")
      if not outputs is None:
        if isinstance(outputs, dict):
          return len(outputs.keys()) > 0

    return False

  def is_viewer(self):
    return self.settings.get("class") == "viewer"

  def input_information(self) -> dict:
    if "inputs" in self.settings:
      inputs = self.settings.get("inputs")
      processed_inputs = {}
      if not inputs is None:
        if isinstance(inputs, dict):
          for k in inputs:
            data = inputs[k]
            if isinstance(data, str):
              d = {}
              data = data.split(".")
              d["type"] = data[0]
              if len(data) >= 2:
                d["subtype"] = data[1]
              data = d
            elif isinstance(data, list):
              d = {}
              if len(data) > 0:
                d["type"] = data[0]
              if len(data) > 1:
                d["subtype"] = data[1]
              data = d

            if isinstance(data, dict):
              if not "display" in data:
                data["display"] = str(k).replace("_", " ").capitalize()
            
            if "type" in data:
              processed_inputs[k] = data

          return processed_inputs

    return {}

  def output_information(self) -> dict:
    if "outputs" in self.settings:
      outputs = self.settings.get("outputs")
      processed_outputs = {}
      if not outputs is None:
        if isinstance(outputs, dict):
          for k in outputs:
            data = outputs[k]
            if isinstance(data, str):
              d = {}
              data = data.split(".")
              d["type"] = data[0]
              if len(data) >= 2:
                d["subtype"] = data[1]
              data = d
            elif isinstance(data, list):
              d = {}
              if len(data) > 0:
                d["type"] = data[0]
              if len(data) > 1:
                d["subtype"] = data[1]
              data = d

            if isinstance(data, dict):
              if not "display" in data:
                data["display"] = str(k).replace("_", " ").capitalize()
            
            if "type" in data:
              processed_outputs[k] = data

          return processed_outputs

    return {}

  def run(self) -> dict:
    if "type" in self._data:
      p_type = self._data.get("type")
      if p_type == PluginType.PYTHON.value:
        return self.run_python()
      elif p_type == PluginType.EXECUTABLE.value:
        return self.run_executable()

  def run_executable(self):
    kwargs = self.settings.get("kwargs", {})
    kwargs.update(self.input_data)

    comms = self.settings.get("commands", [])
    comm = self.settings.get("command")

    if not comm is None:
      comms = [{"command": comm}]

    final_command = None

    for item in comms:
      if not isinstance(item, dict):
        continue

      reqs = item.get("requires")
      if reqs is None:
        final_command = item.get("command")
        break

      if isinstance(reqs, str):
        if not kwargs.get(reqs) is None:
          final_command = item.get("command")
          break

      if isinstance(reqs, list) or isinstance(reqs, tuple):
        failed = False
        for k in reqs:
          if kwargs.get(k) is None:
            failed = True
            break

        if not failed:
          final_command = item.get("command")
          break


    if not final_command is None:
      if isinstance(final_command, list):
        updated_comm = []
        for c in final_command:
          val = c
          if str(c).lower().startswith("$i:"):
            var_name = str(c)[3:]
            if var_name in kwargs:
              c = kwargs[var_name]
              val = kwargs[var_name]
          if str(c).lower().__contains__("<base_dir>"):
            data_path = self._data.get("path")
            val = str(c).replace("<BASE_DIR>", data_path)

          updated_comm.append(val)
        final_command = updated_comm

    if not final_command is None:
      self.on_executable_run(final_command)

    self.on_finished()

  def on_executable_run(self, command):
    subprocess.run(command)

  def run_python(self):
    kwargs = self.settings.get("kwargs", {})
    kwargs.update(self.input_data)
    data_path = self._data.get("path")
    p = pathlib.Path(data_path)
    if not p.exists():
      print(f"plugin data path: {p} does not exist!")
      return

    modules = [str(p.parent.resolve())]
    module_name = p.name
    callback = self.settings.get("callback")

    if callback is None:
      print(f"no callback function specified for plugin")
      return

    function_name = f"{module_name}.{callback}"
    executable = self.settings.get("python")
    if str(executable).strip() == "":
      executable = None
    
    self.on_python_run(function_name=function_name, executable=executable, modules=modules, args=[], kwargs=kwargs)

  def terminate(self):
    if not self.worker is None:
      self.worker.terminate()

  def _process_completed(self, output):
    if "error" in output:
      err = output.get("error")
      self.on_error(str(err))

    elif "result" in output:
      out_info = self.output_information()
      result = output.get("result")

      if isinstance(result, list):
        cnt = 0
        for k in out_info:
          if cnt < len(result):
            out_info[k]["value"] = self.check_data_value(out_info[k]["type"], out_info[k]["subtype"], result[cnt], bool(out_info[k].get("ismultiple")))
          cnt += 1

      elif isinstance(result, dict):
        for k in out_info:
          if k in result:
            out_info[k]["value"] = self.check_data_value(out_info[k]["type"], out_info[k]["subtype"], result[k], bool(out_info[k].get("ismultiple")))

      elif not result is None:
        if len(out_info) == 1:
          for k in out_info:
            out_info[k]["value"] = self.check_data_value(out_info[k]["type"], out_info[k]["subtype"], result, bool(out_info[k].get("ismultiple")))

      output = {}
      for k in out_info:
        if "value" in out_info[k]:
          if not out_info[k].get("value") is None:
            if self.output_prefix != "":
              output[f"{self.output_prefix}_{k}"] = out_info[k]
            else:
              output[k] = out_info[k]

      if not self.is_viewer():
        self.on_completed(output)
    
    self.on_finished()

  def on_error(self, error): # to be handled by inhered class
    self.last_error = error

  def on_completed(self, output): # to be handled by inhered class
    self.last_output = output

  def on_finished(self): # to be handled by inhered class
    pass

  def on_python_run(self, function_name, executable, modules, args, kwargs): # to be handled by inhered class and call _process_completed when done
    if not self.worker is None:
      self.worker.deleteLater()

    self.worker = Worker(function_name=function_name, executable=executable, modulePaths=modules, args=args, kwargs=kwargs, callback=self._process_completed)
    self.worker.start()
    self.worker.join()

  def check_data_value(self, type, subtype, data, ismultiple=False):
    if type == DataType.SCALAR.value:
      try:
        value = data
        if subtype == ScalarType.INT.name:
          value = int(value)
        elif subtype == ScalarType.FLOAT.name:
          value = float(value)
        elif subtype == ScalarType.DATETIME.name:
          value = datetime()
        elif subtype == ScalarType.BOOL.name:
          value = bool(value)

        return value
      except Exception as ex:
        return None

    else:
      if ismultiple:
        if not (isinstance(data, list) or isinstance(data, tuple)):
          data = [data]
        
      if isinstance(data, list) or isinstance(data, tuple):
        d = []
        for dd in data:
          if os.path.exists(str(dd)):
            d.append(dd)
        return d
      else:
        if os.path.exists(str(data)):
          return str(data)

      return None

 
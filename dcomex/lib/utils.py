import importlib, traceback, subprocess
from typing import Tuple
from datetime import datetime

def run_code(mod_name: str, func_name: str, *args, **kwargs) -> dict:
  try:
    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)
    result = func(*args, **kwargs)
    return {"result": result}
  except Exception as ex:
    errtrace = traceback.format_exc()
    return {"error": True, "message": f"{ex}", "trace": str(errtrace)}

def run_command(command):
  subprocess.run(command)

def json_default(obj):
  if isinstance(obj, datetime):
    return {"$date": obj.timestamp()}
  
  return str(obj)

def json_object_hook(obj):
  if isinstance(obj, dict):
    if "$date" in obj:
      return datetime.fromtimestamp(obj.get("$date"))
      
  return obj

executionCode = """
import sys, json, os, importlib, traceback

def write_output(data, filename):
  if not filename is None:
    with open(filename, "w") as json_file:
      json.dump(data, json_file)

try:
  payload = json.loads(sys.stdin.read())
  modules = payload.get("modules", [])
  
  for module in modules:
    sys.path.append(os.path.abspath(module))

  output_file = payload.get("output")

  if not payload is None:
    callback = payload.get("function_name")
    if not callback is None:
      if str(callback).__contains__("."):
        mod_name, func_name = callback.rsplit(".", 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        args = payload.get("args", [])
        kwargs = payload.get("kwargs", {})
        result = func(*args, **kwargs)
        data = {"result": result}
        write_output(data, output_file)
      elif callback in globals():
        func = globals()[callback]
        args = payload.get("args", [])
        kwargs = payload.get("kwargs", {})
        result = func(*args, **kwargs)
        data = {"result": result}
        write_output(data, output_file)
      else:
        err = "Function " + str(callback) + " not found!"
        raise Exception(err)

except Exception as ex:
  errtrace = traceback.format_exc()
  err = "Error " + str(ex)
  data = {"error": {"trace": str(errtrace), "message": err}}
  write_output(data, output_file)
"""
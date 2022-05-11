import json
from lib.plugin_manager import PluginManager
from lib.plugin import Plugin
from lib.data import DataType, ScalarType
import datetime,shlex
from misc import load_json, save_json

def handle_run(args, existing_outputs={}):
  if existing_outputs is None:
    existing_outputs = {}

  plugin_name = args.plugin_name
  input_data = args.inputs
  pmanager = PluginManager()
  pgs = pmanager.find_plugin_by_name(plugin_name)

  if not args.input_file is None:
    input_data.update(load_json(args.input_file))
  
  if len(pgs) == 0:
    print(f"No plugin with name '{plugin_name}' exist!")
    return

  pdata = pgs[0]
  
  p = Plugin(data=pdata, manager=pmanager)

  if p.has_inputs() or p.has_outputs():
    req_inputs = p.input_information()
    processed_input_data = {}

    for in_name in req_inputs:
      in_data = req_inputs[in_name]
      if in_name in input_data:
        in_value = input_data[in_name]

        if type(in_value) == dict:
          in_value = in_value.get("value")

        if in_data.get("type") == DataType.SCALAR.value:
          sub = in_data.get("subtype")
          if sub == ScalarType.FLOAT.value:
            in_value = float(in_value)
          elif sub == ScalarType.INT.value:
            in_value = int(in_value)
          elif sub == ScalarType.BOOL.value:
            in_value = bool(in_value)
          elif sub == ScalarType.DATETIME.value:
            in_value = datetime.datetime.fromisoformat(in_value)

        processed_input_data[in_name] = in_value

      else:
        if in_data.get("required", False) and (not "default" in in_data):
          print(f"input parameter '{in_name}' is required!")
          return
        elif "default" in in_data:
          processed_input_data[in_name] = in_data["default"]
  
    output_prefix = args.prefix
    p.set_inputs(processed_input_data, output_prefix)
  
  p.run()

  if not p.last_error is None:
    print(p.last_error)

  if not p.last_output is None:
    existing_outputs.update(p.last_output)

  if not args.output_file is None:
    save_json(existing_outputs, args.output_file)

  pipe = args.pipe

  if len(pipe) > 0:

    out_maps = args.outputs
    new_inputs = {} if not args.forward_outputs else ({}).update(existing_outputs)
    for out_map in out_maps:
      out_map_value = out_maps[out_map]
      if out_map_value in existing_outputs:
        new_inputs[out_map] = existing_outputs[out_map_value]

    command = ["run"] +  shlex.split(pipe[0]) + ["-i", json.dumps(new_inputs)]

    if len(pipe) > 1:
      for p in pipe[1:]:
        command = command + ["--pipe", p]

    from arg_parser import parse_args
    parsed_args = parse_args(command)

    handle_run(parsed_args, existing_outputs)
    
  

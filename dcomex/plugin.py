from __future__ import print_function
from .misc import load_json, json
from .lib.plugin_manager import PluginManager, PluginType
import os, json, git, shutil

def handle_plugins(args):
  action = args.action

  if action == "create":
    handle_create(args)
  elif action == "install":
    handle_install(args)
  elif action == "remove":
    handle_remove(args)
  elif action == "list":
    handle_list(args)
  elif action == "info":
    handle_info(args)
  elif action == "set":
    handle_set(args)
  else:
    print(f"Action '{action}' not handled!")

def handle_list(args):
  pmanager = PluginManager()
  ps = pmanager.get_plugins()
  print("{:<25} {:<25} {:<25}".format('Name','Display','Path'))
  print("{:<25} {:<25} {:<25}".format('-----','-------','------'))
  for p in ps:
    print("{:<25} {:<25} {:<25}".format(p['name'],p['display'],p['path']))

def handle_info(args):
  pmanager = PluginManager()
  pname = args.plugin_name
  p = pmanager.find_plugin_by_name(pname)

  if len(p) > 0:
    p = p[0]
    sett = p.get("settings")
    p["settings_path"] = sett
    del p["settings"]
    if not sett is None:
      settings = load_json(sett)
      p['settings'] = settings
    print(json.dumps(p, indent=2))
  else:
    print(f"There is no plugin with name '{pname}'")

def handle_set(args):
  pmanager = PluginManager()
  pname = args.plugin_name
  p = pmanager.find_plugin_by_name(pname)

  if len(p) > 0:
    p = p[0]
    kwargs = args.kwargs
    for k in kwargs:
      if k in ["path", "settings", "name", "display", "group", "type", "viewer"]:
        p[k] = kwargs[k]

    pmanager.update_plugin(p, p.doc_id)

  else:
    print(f"There is no plugin with name '{pname}'")

def handle_create(args):
  temp_type = args.type
  temp_path = args.path

  full_path = os.path.abspath(temp_path)
  
  if os.path.isdir(full_path):
    print(f"Directory {full_path} already exsits, enter a path which does not already exist.")
    return

  os.makedirs(full_path, exist_ok=False)

  settings = {
    "inputs": {},
    "outputs": {},
    "kwargs": {},
    "callback": "main",
    "module": ".",
    "python": ""
  }

  if temp_type == "executable":
    settings = {
      "inputs": {
        "raw_input": {}
      },
      "kwargs": {},
      "commands": [
        {
          "command": ["<PATH TO EXECUTABLE WITH ARGS>", "$i:raw_input"],
          "requires": ["raw_input"]
        },
        {
          "command": ["<PATH TO EXECUTABLE WITHOUT ARGS>"]
        }
      ]
    }

  with open(os.path.join(full_path, "settings.json"), "w") as json_file:
    json.dump(settings, json_file, indent=2)

  if temp_type == "python":
    with open(os.path.join(full_path, "__init__.py"), "w") as py_file:
      py_file.write(f"\ndef main(**kwargs):\n\tpass")

def handle_install(args):
  name = args.name
  pth = args.path
  settings = args.settings
  display = args.display
  group = args.group
  is_git = args.git
  is_viewer = args.viewer

  if is_git:
    plugin_path = os.path.join(os.path.expanduser("~"), ".dcomex", "plugins", name)
    repo = git.Repo.clone_from(pth, plugin_path)
    repo.submodule_update()
    pth = plugin_path

  full_path = os.path.abspath(pth)
  set_path = os.path.join(full_path, settings)

  if not os.path.isdir(full_path):
    print(f"Path '{full_path}' does not exist!")
    return

  if not os.path.isfile(set_path):
    print(f"Settings file '{set_path}' does not exist!")
    if is_git:
      shutil.rmtree(path=pth)
    return

  with open(set_path, "r") as json_file:
    data = json.load(json_file)
    ptype = None

    if "module" in data and "callback" in data:
      ptype = PluginType.PYTHON.value
    elif "commands" in data:
      ptype = PluginType.EXECUTABLE.value

    if ptype is None:
      print("Settings file with wrong format!")
      if is_git:
        shutil.rmtree(path=pth)
      return
    
    if not ptype is None:
      pmanager = PluginManager()
      plugin_data = {
        "name": name,
        "path": full_path,
        "settings": set_path,
        "type": ptype,
        "display": name,
        "viewer": is_viewer
      }

      if (not group is None) and str(group).lower() != 'none':
        plugin_data["group"] = group
      
      if (not display is None) and str(display).lower() != 'none':
        plugin_data["display"] = display

      res, mes = pmanager.insert_plugin(plugin_data)
      if not res:
        print(mes)
        if is_git:
          shutil.rmtree(path=pth)

def handle_remove(args):
  names = args.name
  yes = args.yes
  if not yes:
    yes = str(input(f"do you want to remove plugin '{', '.join(names)}' (y/N)?: ")).lower() == 'y'

  if yes:
    pmanager = PluginManager()
    for name in names:  
      p = pmanager.find_plugin_by_name(name=name)
      if len(p) == 0:
        print(f"No plugin with name '{name}' exist!")
      else:
        pmanager.remove_plugin(p[0].doc_id)
        print(f"Plugin {name} successfully removed!")
import os, shutil, subprocess, stat
import tempfile, platform
from .misc import clone_repo, load_json, save_json
from .arg_parser import parse_args
from .plugin import handle_install

GIT_REPO = "https://github.com/giesekow/dcomex-modules.git"
SETUP_FILE = "setup.sh"
PRE_SETUP_FILE = "pre_setup.sh"
INSTALL_FILE = "install.json"

# https://realpython.com/intro-to-pyenv/

IS_INITIALISED_FILE = os.path.join(os.path.expanduser("~"), ".dcomex", "plugins", "is_initialized")
PLUGIN_BASE = os.path.join(os.path.expanduser("~"), ".dcomex", "plugins")
PYENV = os.path.join(os.path.expanduser("~"), ".pyenv", "bin", "pyenv")

SHELL_SCRIPTS = {
  "get_virt_path": [
    "#!/bin/sh\n",
    "\n",
    'eval "$(pyenv init -)"',
    "\n",
    'eval "$(pyenv virtualenv-init -)"',
    "\n",
    'vpath=$(pyenv prefix $1)',
    "\n",
    'echo $vpath'
  ]
}

def copytree(src, dst, symlinks = False, ignore = None):
  if not os.path.exists(dst):
    os.makedirs(dst)
    shutil.copystat(src, dst)
  lst = os.listdir(src)
  if ignore:
    excl = ignore(src, lst)
    lst = [x for x in lst if x not in excl]
  for item in lst:
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if symlinks and os.path.islink(s):
      if os.path.lexists(d):
        os.remove(d)
      os.symlink(os.readlink(s), d)
      try:
        st = os.lstat(s)
        mode = stat.S_IMODE(st.st_mode)
        os.lchmod(d, mode)
      except:
        pass # lchmod not available
    elif os.path.isdir(s):
      copytree(s, d, symlinks, ignore)
    else:
      try:
        shutil.copy2(s, d)
      except Exception as e:
        print(f"Error: {e}")

def handle_init(args):
  if os.path.isfile(IS_INITIALISED_FILE):
    print("Application already initialized!")
    return

  os.makedirs(PLUGIN_BASE, exist_ok=True)

  with tempfile.TemporaryDirectory() as tmp_folder:
    clone_repo(GIT_REPO, tmp_folder)

    # Install pre-req (pyenv)
    command = ["bash", os.path.join(tmp_folder, PRE_SETUP_FILE)]
    subprocess.run(command)

    # Install requirements (pyenv)
    if args.install_requirements:
      command = ["bash", os.path.join(tmp_folder, SETUP_FILE)]
      subprocess.run(command)

    # Load install.json file
    install_data = load_json(os.path.join(tmp_folder, INSTALL_FILE))

    # install envs
    envs = {}
    if "environments" in install_data:
      envs = install_virtual_envs(install_data["environments"], tmp_folder)

    if "plugins" in install_data:
      install_plugins(install_data["plugins"], envs, tmp_folder)
        
def install_virtual_envs(envs, baseDir):
  env_paths = {}

  for env_name in envs:
    env_data = envs[env_name]
    p_version = platform.python_version()

    if "python" in env_data:
      p_version = env_data["python_version"]

    #install python version
    install_python_version(p_version)

    #create virtualenv
    _, env_python = create_virtual_env(p_version, env_name, baseDir)

    # Install requirements
    if "requirements" in env_data:
      requirements = env_data["requirements"]
      if not isinstance(requirements, list):
        requirements = [requirements]

      if len(requirements) > 0:
        command = [env_python, "-m", "pip", "install"]
        for rq in requirements:
          command = command + ["-r", os.path.join(baseDir, rq)]

        subprocess.run(command, cwd=baseDir)

    env_paths[env_name] = env_python

  return env_paths

def install_plugins(plugins, envs, baseDir):
  for plugin_name in plugins:
    plugin = plugins[plugin_name]
    plugin_env = plugin.get("environment")
    plugin_path = plugin.get("path")
    plugin_settings = plugin.get("settings", "settings.json")

    if plugin_path is None:
      continue

    full_path = os.path.join(baseDir, plugin_path)
    settings_file = os.path.join(full_path, plugin_settings)
    
    if not os.path.exists(settings_file):
      continue

    settings = load_json(settings_file)

    if not plugin_env is None and not plugin_env == "":
      if plugin_env in envs:
        settings["python"] = envs[plugin_env]

    os.remove(settings_file)
    save_json(settings, settings_file)

    plugin_base = os.path.join(PLUGIN_BASE, plugin_name)

    if os.path.isdir(plugin_base):
      print(f"Directory {plugin_base} already exist!")
      continue

    copytree(full_path, plugin_base, symlinks=True)
    
    command = ["plugin", "install", plugin_name, plugin_base,
     "-s", os.path.join(plugin_base, plugin_settings),
     "-t", plugin.get("type", "python"),
     "-g", plugin.get("group"),
     "-n", plugin.get("display", plugin_name)]

    if plugin.get("viewer", False):
      command.append("--viewer")

    args = parse_args(command)
    handle_install(args)

def install_python_version(version):
  command = [PYENV, "versions"]
  rc, versions = run_command(command)
  versions = [str(v).strip() for v in versions]

  if not str(version).strip() in versions:
    command = [PYENV, "install", str(version).strip()]
    rc, _ = run_command(command)

  return rc == 0

def create_virtual_env(p_version, env_name, baseDir):
  command = [PYENV, "virtualenv", p_version, env_name]
  rc, _ = run_command(command)
  temp_script = os.path.join(baseDir, 'temp_script.sh')

  with open(temp_script, 'w') as script_file:
    s_script = SHELL_SCRIPTS["get_virt_path"]
    s_script[-3] = f"vpath=$(pyenv prefix {env_name})"
    script_file.writelines(SHELL_SCRIPTS["get_virt_path"])
  
  command = ["sh", temp_script, env_name]
  rc, vpath = run_command(command)

  vpath = os.path.join(vpath[-2], "bin", "python")

  return rc == 0, vpath

def run_command(command):
  result = subprocess.run(command, stdout=subprocess.PIPE)
  return result.returncode, str(result.stdout.decode("utf-8")).split('\n')

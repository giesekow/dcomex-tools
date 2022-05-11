#!/usr/bin/env python3

from __future__ import print_function
import os, argparse, json, sys
from argparse import Action
import yaml
from plugin import handle_plugins
from process import handle_run

INSTALLERS = ['local', 'git']

def dict_load(data):
  data = str(data).strip()
  if not data.startswith("{"):
    data = "{" + data + "}"

  data = ": ".join([s.strip() for s in str(data).split(":")])
  return yaml.load(data, Loader=yaml.FullLoader)

class UpdateAction(Action):
  def __init__(self, option_strings, dest, nargs=None, **kwargs):
    if nargs is not None:
      raise ValueError("nargs not allowed")
    super().__init__(option_strings, dest, **kwargs)

  def __call__(self, parser, namespace, values, option_string=None):
    init_value = getattr(namespace, self.dest, {})
    init_value.update(values)
    setattr(namespace, self.dest, init_value)

def parse_args(params=None):
  parser = argparse.ArgumentParser(description='A Command line tool for the dicomex processing tool', add_help=True)
  subparsers = parser.add_subparsers(dest='submodule')
  
  gui = subparsers.add_parser('gui', description='Open the graphical user interface')
  app_init = subparsers.add_parser('init', description='Initialize the app')
  app_init.add_argument('-r', '--install-requirements', dest='install_requirements', action='store_true',  help='Install requirements in the process [pyenv]')
  
  # Handle plugin submodule
  plugin = subparsers.add_parser('plugin', description='Manage the plugin sub module')
  plugin_subparsers = plugin.add_subparsers(dest='action')
  
  #Handle plugin create action
  plugin_create = plugin_subparsers.add_parser('create', description='Create a template with the required structure for a plugin')
  plugin_create.add_argument('type', metavar='type', type=str, choices=['executable', 'python'], help='The template type to be created [executable, python]')
  plugin_create.add_argument('path', metavar='path', type=str, help='The path to the template to be created!')

  #Handle plugin install action
  plugin_install = plugin_subparsers.add_parser('install', description='Install a plugin')
  plugin_install.add_argument('name', metavar='name', type=str, help='The unique name to the plugin')
  plugin_install.add_argument('path', metavar='path', type=str, help='The path to the plugin, this can be a local folder or a git repo')
  plugin_install.add_argument('-s', '--settings', dest='settings', type=str, default="settings.json",  help='The path to the settings json file relative to the plugin path. Default to "settings.json"')
  plugin_install.add_argument('-t', '--type', dest='type', type=str, default="python",  help='The type of the plugin. Defaults to "python"')
  plugin_install.add_argument('-g', '--group', dest='group', type=str, default=None,  help='The group to install the plugin to. Defaults to None')
  plugin_install.add_argument('-n', '--display', dest='display', type=str, default=None,  help='Plugin display name. Defaults to unique name')
  plugin_install.add_argument('--git', dest='git', action='store_true',  help='Installation path is a git repo')
  plugin_install.add_argument('--viewer', dest='viewer', action='store_true',  help='Installation path is a git repo')

  #Handle plugin remove action
  plugin_remove = plugin_subparsers.add_parser('remove', description='Remove a plugin')
  plugin_remove.add_argument('name', metavar='name', type=str, nargs='*', help='The names of plugins to be removed')
  plugin_remove.add_argument('-y', dest='yes', action='store_true',  help='Answer yes to all questions')

  #Handle plugin list action
  plugin_list = plugin_subparsers.add_parser('list', description='List installed plugins')

  #Handle plugin info action
  plugin_info = plugin_subparsers.add_parser('info', description='List installed plugins')
  plugin_info.add_argument('plugin_name', metavar='plugin_name', type=str, help='The plugin to display the information for')

  #Handle plugin set action
  plugin_set = plugin_subparsers.add_parser('set', description='List installed plugins')
  plugin_set.add_argument('plugin_name', metavar='plugin_name', type=str, help='The plugin to display the information for')
  plugin_set.add_argument('-k', '--kwarg', dest='kwargs', action=UpdateAction, type=dict_load, default={}, help='Named set arguments for the plugin in yaml or json format')



  #Handle process submodule
  process = subparsers.add_parser('run', description='Invoke the processing engine')
  process.add_argument('plugin_name', metavar='plugin_name', type=str, help='The plugin to invoke')
  process.add_argument('-i', '--input', dest='inputs', action=UpdateAction, type=dict_load, default={}, help='named input arguments for the plugin in yaml or json format')
  process.add_argument('-o', '--output', dest='outputs', action=UpdateAction, type=dict_load, default={}, help='output mapping in yaml or json format, useful for piping plugins')
  process.add_argument('-p', '--prefix', dest='prefix', default="", type=str, help='prefix for outputs from the plugin, defaults to empty string')
  process.add_argument('--input-file', dest='input_file', default=None, type=str, help='Path to a json file containing input information')
  process.add_argument('--output-file', dest='output_file', default=None, type=str, help='Path to a json file to store the output information')
  process.add_argument('--pipe', dest='pipe', action='append', default=[], type=str, help='pipe another run command, a string which takes all the existing options')
  process.add_argument('--forward-outputs', dest='forward_outputs', action='store_true',  help='Forward previous outputs to piped plugin')

  if params is None:
    args = parser.parse_args()
    return args
  else:
    args = parser.parse_args(params)
    return args
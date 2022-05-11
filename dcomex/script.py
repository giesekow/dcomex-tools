#!/usr/bin/env python3

from __future__ import print_function
from .arg_parser import parse_args
from .initialize import handle_init
from .plugin import handle_plugins
from .process import handle_run

def main():
  args = parse_args()
  submodule = args.submodule
  if submodule == "gui":
    handle_gui(args)
  elif submodule == "plugin":
    handle_plugins(args)
  elif submodule == "run":
    handle_run(args)
  elif submodule == "init":
    handle_init(args)
  else:
    print(f"Submodule {submodule} has no handler!")

def handle_gui(args):
  from .gui import showGui
  showGui()


if __name__ == "__main__":
  main()
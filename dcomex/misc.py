import os, json, git, shutil, tempfile

def load_json(filepath):
  data = {}
  try:
    with open(filepath, 'r') as json_file:
      data = json.load(json_file)
  except Exception as e:
    print(f"Error loading json file:\n{e}")

  return data

def save_json(data, filepath):
  with open(filepath, 'w') as json_file:
    json.dump(data, json_file, indent=2)

def clone_repo(url, folderPath):
  repo = git.Repo.clone_from(url, folderPath)
  repo.submodule_update()
  return folderPath


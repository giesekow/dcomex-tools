#!/bin/bash
pip install build

rm -rf build
rm -rf dist
rm -rf *.egg-info
python3 -m build
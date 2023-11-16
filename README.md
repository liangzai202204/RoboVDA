# Python Script to Executable for rbk

This repository provides a Shell script to easily convert Python scripts to executable files on Linux systems.

## Dependencies

This script requires having installed on your system:

1. Python
2. PIP (Python package installer)
3. PyInstaller (will be installed automatically if not found)

## Usage

1. Ensure your python script file has the shebang line (`#!/usr/bin/env python3`) at the beginning. Here, `app.py` is used as an example Python script.
2. Make the `make_app.sh` Shell script executable by running:
   ```
   chmod +x make_app.sh
   ```
3. Run the script with your Python script file as an argument:
   ```
   ./make_app.sh app.py
   ```
4. The Python script will be converted into an executable file under the `dist/` directory.

Please note: The Shell script will check if PyInstaller is installed on your system. If not, it will attempt to install it. Make sure you are connected to the internet.
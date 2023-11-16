#!/bin/bash
# Get python script name from the command line argument
PYTHON_SCRIPT=$1

# Add execute permissions to the python script
chmod +x $PYTHON_SCRIPT

# Check if PyInstaller is installed, if not, install it.
if ! [ -x "$(command -v pyinstaller)" ]; then
  pip install pyinstaller
fi

# Use PyInstaller to create an executable
pyinstaller --onefile $PYTHON_SCRIPT
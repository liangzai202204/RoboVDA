![src](./assets/src.webp)

# Python Script to Executable for rbk

This repository provides a Shell script to easily convert Python scripts to executable files on Linux systems.

## Dependencies

This script requires having installed on your system:

1. Python
2. PIP (Python package installer)
3. PyInstaller (will be installed automatically if not found)

## Usage

1. Ensure your python script file has the shebang line (`#!/usr/bin/env python3`) at the beginning. Here, `app.py` is used as an example Python script.
2. Make the Shell script executable by running:
   ```bash
   pyinstaller --onefile src/RoboVda.py
   ```
3. The Python script will be converted into an executable file under the `dist/` directory.

Please note: The Shell script will check if PyInstaller is installed on your system. If not, it will attempt to install it. Make sure you are connected to the internet.

## make .deb and zip

1. chmod
   ```bash
   chmod 775 SeerRobotics/RoboVda-SRC/DEBIAN/postinst
   chmod 775 SeerRobotics/RoboVda-SRC/DEBIAN/prerm
   chmod 775 SeerRobotics/RoboVda-SRC/DEBIAN/preinst
   chmod 775 SeerRobotics/RoboVda-SRC/DEBIAN/postrm
   cp dist/RoboVda SeerRobotics/RoboVda-SRC/usr/local/SeerRobotics/vda/
   ```

2. make deb && make zip
   ```bash
   version=`grep "^Version:" SeerRobotics/RoboVda-SRC/DEBIAN/control | awk '{print $2}'`
   current_time=$(date +"%Y%m%d%H%M%S")
   filename="RoboVda-SRC-v${version}-${current_time}"
   dpkg-deb --build SeerRobotics/RoboVda-SRC ${filename}.deb

   zip -r ${filename}.zip ${filename}.deb
   ```

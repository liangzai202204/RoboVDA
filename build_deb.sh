#!/bin/bash
if [ ! -d "SeerRobotics" ]; then  # 检查目录是否存在
  mkdir SeerRobotics
else
  echo "rm -rf SeerRobotics"
  rm -rf SeerRobotics  # 删除整个目录及其内容
fi
mkdir -p SeerRobotics/RoboVda/DEBIAN
cp control SeerRobotics/RoboVda/DEBIAN/
mkdir -p SeerRobotics/RoboVda/usr/local/SeerRobotics/vda

mkdir -p SeerRobotics/RoboVda/usr/local/SeerRobotics/vda/robotModel  # 创建目录（包括父目录）
mkdir -p SeerRobotics/RoboVda/usr/local/SeerRobotics/vda/robotModel  # 创建目录（包括父目录）
mkdir -p SeerRobotics/RoboVda/usr/local/SeerRobotics/vda/robotModel  # 创建目录（包括父目录）
mkdir -p SeerRobotics/RoboVda/etc/systemd/system  # 创建目录（包括父目录）
cp startup_vda.service SeerRobotics/RoboVda/etc/systemd/system/
cp dist/RoboVda SeerRobotics/RoboVda/usr/local/SeerRobotics/vda
echo "chmod +777 RoboVda."
chmod +777 SeerRobotics/RoboVda/usr/local/SeerRobotics/vda/RoboVda
cd SeerRobotics
echo "build RoboVda running."
dpkg-deb --build RoboVda
echo "build RoboVda.deb OK."
echo "build zip."
mkdir -p vda
cd ..
cp RoboVda.sh SeerRobotics/vda/
cp config.ini SeerRobotics/vda/


folder_name="SeerRobotics"  # 替换为实际的文件夹名称
zip_file_name="SeerRobotics.zip"  # 替换为实际的压缩文件名称

if [ -d "$folder_name" ]; then  # 检查文件夹是否存在
    zip -r "$zip_file_name" "$folder_name" -x "$folder_name/RoboVda/*"  # 压缩文件夹并排除指定的文件夹
else
    echo "Folder $folder_name does not exist."
fi


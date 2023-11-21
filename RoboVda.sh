#!/bin/bash

# 检查是否已经有相同的程序在运行
if pgrep -f "RoboVda" >/dev/null; then
    echo "RoboVda is already running."
    echo seer | sudo -S pkill -f "RoboVda"  # 终止已经在运行的进程
else
    if [ ! -d "/usr/local/SeerRobotics/vda/scripts-logs" ]; then  # 检查目录是否存在
        echo seer | sudo -S mkdir -p /usr/local/SeerRobotics/vda/robotModel  # 创建目录（包括父目录）
    fi
    if [ ! -d "/usr/local/SeerRobotics/vda/robotModel" ]; then  # 检查目录是否存在
        echo seer | sudo -S mkdir -p /usr/local/SeerRobotics/vda/robotModel  # 创建目录（包括父目录）
    fi
        if [ ! -d "/usr/local/SeerRobotics/vda/robotMap" ]; then  # 检查目录是否存在
        echo seer | sudo -S mkdir -p /usr/local/SeerRobotics/vda/robotModel  # 创建目录（包括父目录）
    fi
    cd /usr/local/SeerRobotics/vda/  # 切换到程序所在目录
    echo seer | sudo -S ./RoboVda  # 运行 Python 程序
fi

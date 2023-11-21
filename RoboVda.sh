#!/bin/bash

# 检查是否已经有相同的程序在运行

cd /usr/local/SeerRobotics/vda/  # 切换到程序所在目录
echo seer | sudo -S ./RoboVda  # 运行 Python 程序


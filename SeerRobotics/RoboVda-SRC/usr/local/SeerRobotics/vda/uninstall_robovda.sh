#!/bin/bash

# 列出已安装的软件包并通过 grep 进行筛选
packages=$(dpkg -l | grep RoboVda)

# 检查筛选结果是否为空
if [ -z "$packages" ]; then
  echo "RoboVda 软件包未安装"
else
  # 循环遍历找到的软件包并执行卸载操作
  while read -r package; do
    package_name=$(echo "$package" | awk '{print $2}')
    sudo dpkg -r "$package_name"
    echo "已卸载软件包: $package_name"
  done <<< "$packages"
fi


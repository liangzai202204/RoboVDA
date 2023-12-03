#!/bin/bash

# 查找 RoboVda 的进程ID（PID）
PID=$(ps aux | grep RoboVda | grep -v grep | awk '{print $2}')

# 如果存在进程ID，则终止进程
if [[ ! -z "$PID" ]]; then
  echo "Terminating RoboVda process (PID: $PID)..."
  kill $PID
fi

## 切换到 RoboVda 程序所在目录
#cd /usr/local/SeerRobotics/vda/
#
## 以后台进程的方式重新启动 RoboVda
#sudo ./RoboVda

echo "RoboVda restarted successfully."

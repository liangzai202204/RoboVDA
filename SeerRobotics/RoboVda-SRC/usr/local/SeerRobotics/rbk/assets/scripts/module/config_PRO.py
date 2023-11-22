# -*- coding: utf-8 -*-
# @Request : 用于 测试 resetGoForkPath 和 goForkPath 接口
# @Version: 1.0
import enum
import json
import math
import os
import stat
import time

import syspy.goPath as goPath
from syspy.rbkSim import SimModule
from syspy.rbk import MoveStatus, BasicModule, ParamServer, Pos2Base
from syspy.robot import ModuleTool
"""
####BEGIN DEFAULT ARGS####
{    
    "operation": {
        "value": "",
        "default_value": [
            "setting", "creat_server","creat_start_script","mkdir"
        ],
        "tips": "tips",
        "type": "complex"
    },
    "mqtt_host": {
        "value": "127.0.0.1",
        "default_value": "127.0.0.1",
        "tips": "tips",
        "type": "string"
    },
    "mqtt_port": {
    "value":1883,
        "default_value": 1883,
        "tips": "tips",
        "type": "int"
    },
        "mqtt_transport": {
        "value":60,
        "default_value": 60,
        "tips": "tips",
        "type": "int"
    },
    "robot_ip": {
        "value": "127.0.0.1",
        "default_value": "127.0.0.1",
        "tips": "tips",
        "type": "string"
    },
    "order_topic": {
        "value": "robot/order",
        "default_value": "robot/order",
        "tips": "tips",
        "type": "string"
    },
    "state_topic": {
        "value": "robot/state",
        "default_value": "robot/state",
        "tips": "tips",
        "type": "string"
    },    
    "visualization_topic": {
        "value": "robot/visualization",
        "default_value": "robot/visualization",
        "tips": "tips",
        "type": "string"
    },
    "instantActions_topic": {
        "value": "robot/instantActions",
        "default_value": "robot/instantActions",
        "tips": "tips",
        "type": "string"
    },
    "factsheet_topic": {
        "value": "robot/factsheet",
        "default_value": "robot/factsheet",
        "tips": "tips",
        "type": "string"
    },
    "connection_topic": {
        "value": "robot/connection",
        "default_value": "robot/order",
        "tips": "tips",
        "type": "string"
    },
       "web_host": {
        "value": "localhost",
        "default_value": "localhost",
        "tips": "tips",
        "type": "string"
    },
    "web_port": {
        "value":5000,
        "default_value": 5000,
        "tips": "tips",
        "type": "int"
    },
    "state_report_frequency": {
        "value":1,
        "default_value": 1,
        "tips": "tips",
        "type": "int"
    },
    "config_path": {
        "value": "/usr/local/SeerRobotics/vda",
        "default_value": "/usr/local/SeerRobotics/vda",
        "tips": "tips",
        "type": "string"
    },
    "start_script_path": {
        "value": "/usr/local/SeerRobotics/vda",
        "default_value": "/usr/local/SeerRobotics/vda",
        "tips": "tips",
        "type": "string"
    },
    "start_server_path": {
        "value": "/etc/systemd/system",
        "default_value": "/etc/systemd/system",
        "tips": "tips",
        "type": "string"
    },
    "data":{
        "value": {
                "mqtt_host": "127.0.0.1",
                "mqtt_port": 1883,
                "web_host": "localhost",
                "state_report_frequency": 1,
                "web_port": 5000,
                "mqtt_transport": 60,
                "order_topic": "robot/order",
                "state_topic": "robot/state",
                "visualization_topic": "robot/visualization",
                "connection_topic": "robot/connection",
                "instantActions_topic": "robot/instantActions",
                "factsheet_topic": "robot/factsheet",
                "config_path": "/usr/local/SeerRobotics/vda",
                "start_script_path": "/usr/local/SeerRobotics/vda",
                "start_server_path": "/etc/systemd/system"
            },
        "default_value": "",
        "tips": "tips",
        "type": "json"
    }
}

####END DEFAULT ARGS####
"""
class Module(BasicModule):
    def __init__(self, r: SimModule, args):
        super().__init__()
        self.motor_name = "test"
        self.init = True
        self.state = {}
        self.init_time = time.time()

    def periodRun(self, r: SimModule):
        # self.state["task"] = r.moveTask()
        # self.state["taskSTATUS"] = r.getCurrentTaskStatus()
        # # if ModuleTool.check_DI(r,2):
        # #     r.stopRobot(True)
        r.setInfo(json.dumps(self.state))
        r.logInfo(json.dumps(self.state))
        return True

    def run(self, r: SimModule, args: dict):
        if "operation" in args:
            default_config = {
                "mqtt_host": "127.0.0.1",
                "mqtt_port": 1883,
                "web_host": "localhost",
                "state_report_frequency": 1,
                "web_port": 5000,
                "mqtt_transport": 60,
                "order_topic": "robot/order",
                "state_topic": "robot/state",
                "visualization_topic": "robot/visualization",
                "connection_topic": "robot/connection",
                "instantActions_topic": "robot/instantActions",
                "factsheet_topic": "robot/factsheet",
                "config_path": "/usr/local/SeerRobotics/vda",
                "start_script_path": "/usr/local/SeerRobotics/vda",
                "start_server_path": "/etc/systemd/system"
            }
            if args["operation"] == "setting":
                # 设置默认数值


                # 使用默认值覆盖传入的参数
                config = {key: args.get(key, default_config[key]) for key in default_config}

                # 格式化配置内容
                config_content = f"""
[mqtt]
mqtt_host = {config['mqtt_host']}
mqtt_port = {config['mqtt_port']}
mqtt_transport = {config['mqtt_transport']}

[topic]
order = {config['order_topic']}
state = {config['state_topic']}
visualization = {config['visualization_topic']}
connection = {config['connection_topic']}
instantactions = {config['instantActions_topic']}
factsheet = {config['factsheet_topic']}

[robot]
robot_ip = {config['mqtt_host']}
mode = 2
robot_type = 1

[web]
web_host = {config['web_host']}
web_port = {config['web_port']}

[network]
state_report_frequency = {config['state_report_frequency']}
                        """
                # 如果路径不存在就创建
                if not os.path.exists(config['config_path']):
                    os.makedirs(config['config_path'])
                # 将配置内容写入文件
                with open(os.path.join(config['config_path'], 'config.ini'), 'w') as file:
                    file.write(config_content)
                os.chmod(os.path.join(config['config_path'], 'config.ini'),
                         stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
                # 更新状态和日志
                self.status = MoveStatus.FINISHED
            elif args["operation"] == "creat_server":
                if not os.path.exists(default_config['start_server_path']):
                    os.makedirs(default_config['start_server_path'])
                # 将配置内容写入文件
                with open(os.path.join(default_config['start_server_path'], 'startup_vda.service'), 'w') as file:
                    file.write(START_SERVER)
                os.chmod(os.path.join(default_config['start_server_path'], 'startup_vda.service'),
                         stat.S_IRWXU |stat.S_IRWXG | stat.S_IRWXO)
                os.system(f"echo seer | sudo -S systemctl enable startup_vda")
                os.system(f"echo seer | sudo -S systemctl start startup_vda")
                # 更新状态和日志
                self.status = MoveStatus.FINISHED
            elif args["operation"] == "creat_start_script":
                if not os.path.exists(os.path.join("/usr/local/SeerRobotics/vda", 'RoboVda.sh')):
                    with open(os.path.join("/usr/local/SeerRobotics/vda", 'RoboVda.sh'), 'w') as file:
                        file.write(START_SCRIPT)
                os.chmod(os.path.join("/usr/local/SeerRobotics/vda", 'RoboVda.sh'),
                         stat.S_IRWXU |stat.S_IRWXG | stat.S_IRWXO)
                os.chmod(os.path.join("/usr/local/SeerRobotics/vda", 'RoboVda'),
                         stat.S_IRWXU |stat.S_IRWXG | stat.S_IRWXO)
                os.chmod(os.path.join("/usr/local/SeerRobotics/vda", 'config.ini'),
                         stat.S_IRWXU |stat.S_IRWXG | stat.S_IRWXO)
                # 更新状态和日志
                self.status = MoveStatus.FINISHED
            elif args["operation"] == "mkdir":
                os.system(f"echo seer | sudo -S mkdir /usr/local/SeerRobotics/vda && chmod 777 /usr/local/SeerRobotics/vda")
                os.system(f"echo seer | sudo -S mkdir /usr/local/SeerRobotics/vda/scripts-logs && chmod 777 /usr/local/SeerRobotics/vda/scripts-logs")
                os.system(f"echo seer | sudo -S mkdir /usr/local/SeerRobotics/vda/robotMap && chmod 777 /usr/local/SeerRobotics/vda/robotMap")
                os.system(f"echo seer | sudo -S mkdir /usr/local/SeerRobotics/vda/robotModel && chmod 777 /usr/local/SeerRobotics/vda/robotModel")
                # 生成启动脚本
        r.setInfo(json.dumps(self.state))
        r.logInfo(json.dumps(self.state))

        return self.status

START_SERVER ="""
[Unit]
Description=/usr/local/SeerRobotics/vda/RoboVda.sh
ConditionPathExists=/usr/local/SeerRobotics/vda/RoboVda.sh
After=network.target

[Service]
ExecStart=/usr/local/SeerRobotics/vda/RoboVda.sh
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""

START_SCRIPT = """
#!/bin/bash
cd /usr/local/SeerRobotics/vda  # 切换到程序所在目录
echo seer | sudo -S ./RoboVda  # 运行 Python 程序
"""


if __name__ == '__main__':
    pass
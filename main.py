import argparse
import configparser
import os
import sys
from rbklib import rbklibPro
from log.log import MyLogger
from serve.mqtt_server import RobotServer


def read_config():
    config = configparser.ConfigParser()

    # 读取配置文件
    if not os.path.exists('config.ini'):
        # 创建新的配置文件
        config.add_section('mqtt')
        config.set('mqtt', 'mqtt_host', 'localhost')
        config.set('mqtt', 'mqtt_port', '1883')
        config.set('mqtt', 'mqtt_transport', 'tcp')

        config.add_section('topic')
        config.set('topic', 'order', 'robot/order')
        config.set('topic', 'state', 'robot/state')
        config.set('topic', 'visualization', 'robot/visualization')
        config.set('topic', 'connection', 'robot/connection')
        config.set('topic', 'instantActions', 'robot/instantActions')
        config.set('topic', 'factsheet', 'robot/factsheet')

        config.add_section('robot')
        config.set('robot', 'robot_ip', '192.168.0.1')
        config.set('robot', 'mode', '0')
        config.set('robot', 'robot_type', '1')

        config.add_section('web')
        config.set('web', 'web_host', 'localhost')
        config.set('web', 'web_port', '5000')
        config.add_section('network')
        config.set('network', 'state_report_frequency', '1')

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    config.read('config.ini')
    print(config.sections())

    return config


def config_params():
    c = read_config()
    arg = {
        "mqtt_host": c.get('mqtt', 'mqtt_host'),
        "mqtt_port": c.getint('mqtt', 'mqtt_port'),
        "mqtt_transport": c.get('mqtt', 'mqtt_transport'),
        "robot_ip": c.get('robot', 'robot_ip'),
        "robot_type": c.getint('robot', 'robot_type'),
        "mode": c.getint('robot', 'mode'),
        'web_host': c.get('web', 'web_host'),
        "web_port": c.getint('web', 'web_port'),
        'mqtt_topic_order': c.get('topic', 'order'),
        'mqtt_topic_state': c.get('topic', 'state'),
        'mqtt_topic_visualization': c.get('topic', 'visualization'),
        'mqtt_topic_connection': c.get('topic', 'connection'),
        "mqtt_topic_instantActions": c.get('topic', 'instantActions'),
        "mqtt_topic_factsheet": c.get('topic', 'factsheet'),
        "state_report_frequency": c.getint('network', 'state_report_frequency')
    }
    print(arg)
    return arg


if __name__ == "__main__":
    # 创建配置文件
    args = config_params()
    # 启动服务
    rbk = rbklibPro.Rbk(args.get("robot_ip"))
    args["rbk"] = rbk
    s = RobotServer(**args)
    # 运行服务
    s.run()

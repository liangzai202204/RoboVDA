import argparse
import configparser
import os
import sys

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

        config.add_section('web')
        config.set('web', 'web_host', 'localhost')
        config.set('web', 'web_port', '5000')
        config.set('network', 'state_report_frequency', '1')

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    config.read('config.ini')
    return config


def config_params():
    c = read_config()
    parser = argparse.ArgumentParser()
    # 添加参数
    parser.add_argument("--mqtt_host", default=c.get('mqtt', 'mqtt_host'), help="name")
    parser.add_argument("--mqtt_port", default=c.getint('mqtt', 'mqtt_port'), type=int, help="port")
    parser.add_argument("--mqtt_transport", default=c.get('mqtt', 'mqtt_transport'), choices=("tcp", "websockets"),
                        help="TCP")
    parser.add_argument("--logg", default=MyLogger(), help="log")
    parser.add_argument("--mqtt_topic_order", default=c.get('topic', 'order'), type=str, nargs='?', help="topic")
    parser.add_argument("--mqtt_topic_state", default=c.get('topic', 'state'), type=str, nargs='?', help="topic")
    parser.add_argument("--mqtt_topic_visualization", default=c.get('topic', 'visualization'), type=str, nargs='?',
                        help="topic")
    parser.add_argument("--mqtt_topic_connection", default=c.get('topic', 'connection'), type=str, nargs='?',
                        help="topic")
    parser.add_argument("--mqtt_topic_instantActions", default=c.get('topic', 'instantActions'), type=str,
                        nargs='?', help="topic")
    parser.add_argument("--mqtt_topic_factsheet", default=c.get('topic', 'factsheet'), type=str, nargs='?',
                        help="topic")
    parser.add_argument("--robot_ip", default=c.get('robot', 'robot_ip'), help="robot_ip")
    parser.add_argument("--mode", default=c.getint('robot', 'mode'), type=int, help="mode")
    parser.add_argument("--web_host", default=c.get('web', 'web_host'), help="web_host")
    parser.add_argument("--web_port", default=c.get('web', 'web_port'), help="web_port")

    parser.add_argument("--state_report_frequency", default=c.get('network', 'state_report_frequency'),
                        type=int,help="state_report_frequency")

    return parser.parse_args()


if __name__ == "__main__":
    # 创建配置文件
    args = config_params()
    # 启动服务
    s = RobotServer(**vars(args))
    # 运行服务
    s.run()


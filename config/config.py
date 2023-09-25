import configparser
import os

class Config:
    args = dict
    args_mqtt = dict
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.read_config()

    def read_config(self):
        # 读取配置文件
        if not os.path.exists('config.ini'):
            # 创建新的配置文件
            self.config.add_section('mqtt')
            self.config.set('mqtt', 'mqtt_host', 'localhost')
            self.config.set('mqtt', 'mqtt_port', '1883')
            self.config.set('mqtt', 'mqtt_transport', 'tcp')

            self.config.add_section('topic')
            self.config.set('topic', 'order', 'robot/order')
            self.config.set('topic', 'state', 'robot/state')
            self.config.set('topic', 'visualization', 'robot/visualization')
            self.config.set('topic', 'connection', 'robot/connection')
            self.config.set('topic', 'instantActions', 'robot/instantActions')
            self.config.set('topic', 'factsheet', 'robot/factsheet')

            self.config.add_section('robot')
            self.config.set('robot', 'robot_ip', '192.168.0.1')
            self.config.set('robot', 'mode', '0')
            self.config.set('robot', 'robot_type', '1')

            self.config.add_section('web')
            self.config.set('web', 'web_host', 'localhost')
            self.config.set('web', 'web_port', '5000')
            self.config.add_section('network')
            self.config.set('network', 'state_report_frequency', '1')

            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

        self.config.read('config.ini')
        print(self.config.sections())

    @property
    def configs(self):
        self.args = {
            "mqtt_host": self.config.get('mqtt', 'mqtt_host'),
            "mqtt_port": self.config.getint('mqtt', 'mqtt_port'),
            "mqtt_transport": self.config.get('mqtt', 'mqtt_transport'),
            "robot_ip": self.config.get('robot', 'robot_ip'),
            "robot_type": self.config.getint('robot', 'robot_type'),
            "mode": self.config.getint('robot', 'mode'),
            'web_host': self.config.get('web', 'web_host'),
            "web_port": self.config.getint('web', 'web_port'),
            'mqtt_topic_order': self.config.get('topic', 'order'),
            'mqtt_topic_state': self.config.get('topic', 'state'),
            'mqtt_topic_visualization': self.config.get('topic', 'visualization'),
            'mqtt_topic_connection': self.config.get('topic', 'connection'),
            "mqtt_topic_instantActions": self.config.get('topic', 'instantActions'),
            "mqtt_topic_factsheet": self.config.get('topic', 'factsheet'),
            "state_report_frequency": self.config.getfloat('network', 'state_report_frequency')
        }
        return self.args

    def config_mqtt(self):
        self.args_mqtt = {
            "mqtt_host": self.config.get('mqtt', 'mqtt_host'),
            "mqtt_port": self.config.getint('mqtt', 'mqtt_port'),
            "mqtt_transport": self.config.get('mqtt', 'mqtt_transport'),
            'mqtt_topic_order': self.config.get('topic', 'order'),
            'mqtt_topic_state': self.config.get('topic', 'state'),
            'mqtt_topic_visualization': self.config.get('topic', 'visualization'),
            'mqtt_topic_connection': self.config.get('topic', 'connection'),
            "mqtt_topic_instantActions": self.config.get('topic', 'instantActions'),
            "mqtt_topic_factsheet": self.config.get('topic', 'factsheet'),
        }
        return self.args_mqtt


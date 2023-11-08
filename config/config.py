import configparser
import os
import stat


class Config:
    args = dict
    args_mqtt = dict

    def __init__(self, file_path=None):
        if not file_path:
            if os.name == 'nt':  # Windows系统
                self.file_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            elif os.name == 'posix':  # Linux或者Mac OS系统
                self.file_path = '/usr/local/SeerRobotics/vda'
        else:
            self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.read_config()

    def read_config(self):
        # 读取配置文件
        try:
            if not os.path.exists(os.path.join(self.file_path, 'config.ini')):
                # 创建新的配置文件
                if not os.path.exists(self.file_path):
                    os.makedirs(self.file_path)
                # 将配置内容写入文件
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
                self.config.add_section('script')
                self.config.set('script', 'script_name', 'script.py')
                with open(os.path.join(self.file_path, 'config.ini'), 'w') as configfile:
                    self.config.write(configfile)
                os.chmod(os.path.join(self.file_path, 'config.ini'),
                         stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
            self.config.read(os.path.join(self.file_path, 'config.ini'))
            print(self.config.sections())
        except Exception as e:
            print("config", e)

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
            "state_report_frequency": self.config.getfloat('network', 'state_report_frequency'),
            "script_name": self.config.get('script', 'script_name')
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

    def config_script(self):
        return {
            "script_name":self.config.get('script', 'script_name')
        }


if __name__ == '__main__':
    # c = Config()
    # c.read_config()
    pass
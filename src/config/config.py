import configparser
import os
import stat


class Config:
    """
    配置文件類，初始化時讀取配置文件，如果沒有則使用默認參數
    """
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_transport: str = "tcp"
    robot_ip: str = "localhost"
    robot_type: int = 1
    mode: int = 0
    web_host: str = "localhost"
    web_port: int = 5000
    mqtt_topic_order: str = 'robot/order'
    mqtt_topic_state: str = 'robot/state'
    mqtt_topic_visualization: str = 'robot/visualization'
    mqtt_topic_connection: str = 'robot/connection'
    mqtt_topic_instantActions: str = 'robot/instantActions'
    mqtt_topic_factsheet: str = 'robot/factsheet'
    state_report_frequency: float = 1.1
    script_name: str = 'script.py'

    def __init__(self, file_path=None):
        if not file_path:
            if os.name == 'nt':  # Windows系统
                self.file_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            elif os.name == 'posix':  # Linux或者Mac OS系统
                self.file_path = '/usr/local/SeerRobotics/vda'
        else:
            self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.init_config()

    def init_config(self):
        # 读取配置文件
        try:
            if os.path.exists(os.path.join(self.file_path, 'config.ini')):
                self.config.read(os.path.join(self.file_path, 'config.ini'))
                print(self.config.sections())
                self.configs()
        except Exception as e:
            print("config", e)

    def configs(self):
        self.mqtt_host = self.config.get('mqtt', 'mqtt_host')
        self.mqtt_port = self.config.getint('mqtt', 'mqtt_port')
        self.mqtt_transport = self.config.get('mqtt', 'mqtt_transport')
        self.robot_ip = self.config.get('robot', 'robot_ip')
        self.robot_type = self.config.getint('robot', 'robot_type')
        self.mode = self.config.getint('robot', 'mode')
        self.web_host = self.config.get('web', 'web_host')
        self.web_port = self.config.getint('web', 'web_port')
        self.mqtt_topic_order = self.config.get('topic', 'order')
        self.mqtt_topic_state = self.config.get('topic', 'state')
        self.mqtt_topic_visualization = self.config.get('topic', 'visualization')
        self.mqtt_topic_connection = self.config.get('topic', 'connection')
        self.mqtt_topic_instantActions = self.config.get('topic', 'instantActions')
        self.mqtt_topic_factsheet = self.config.get('topic', 'factsheet')
        self.state_report_frequency = self.config.getfloat('network', 'state_report_frequency')
        self.script_name = self.config.get('script', 'script_name')



if __name__ == '__main__':
    # c = Config()
    # print(c.mqtt_host)
    pass

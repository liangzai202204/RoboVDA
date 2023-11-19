import configparser
import os
import time
import unittest
import paho.mqtt.client as mqtt

from type.VDA5050 import order, state


def get_mqtt_ip():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.getcwd()), 'config.ini')
    # 读取配置文件
    config.read(config_path)
    ip = config.get('mqtt', 'mqtt_host')
    print("ip:",ip)
    return ip


def get_order_topic():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.getcwd()), 'config.ini')
    # 读取配置文件
    config.read(config_path)
    order = config.get('topic', 'order')
    return order

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_creat_order_jackload_1(self):
        import json
        path_to_B = os.path.abspath("../VDAExample/order/jack")

        json_filename = 'Transport Order 3066 CubicBeizer2_jackLoad.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            client = mqtt.Client()
            client.connect(get_mqtt_ip(), 1883, 60)
            client.publish("robot/order", json.dumps(json_content))


    def test_creat_order_jackunload_1(self):
        import json
        path_to_B = os.path.abspath("../VDAExample/order/jack")

        json_filename = 'Transport Order 3066 CubicBeizer2_jackUnload.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            client = mqtt.Client()
            client.connect(get_mqtt_ip(), 1883, 60)
            client.publish("robot/order", json.dumps(json_content))





if __name__ == '__main__':
    # unittest.main()
    print(182323-67996)
    print((182323-67996)/1000)

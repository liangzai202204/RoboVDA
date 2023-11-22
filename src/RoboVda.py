import asyncio
import threading

from src.rbklib.rbklibPro import Rbk
from src.serve.handleTopic import HandleTopic
from src.serve.robot import Robot
from src.serve.mqttServer import MqttServer
from src.serve.httpServer import HttpServer
from src.config.config import Config
from src.serve.topicQueue import EventLoop


class RoboVda:
    config_class = Config
    rbk_lib_class = Rbk
    MqttServer_class = MqttServer
    robot_order_class = HandleTopic
    robot_class = Robot
    http_server_class = HttpServer

    def __init__(self):
        self.config = self.get_configs()
        self.rbk = self.creat_rbk()
        self.robot = self.creat_robot()
        self.robot_order = self.creat_robot_order()
        self.mqtt_server = self.creat_mqtt_server()
        self.http_server = self.creat_http_server()

        # 线程设置
        self.rbk_connect_t = threading.Thread(target=self.rbk.connect, name="rbk connect")

        # self.loop = asyncio.new_event_loop()
        # self.robot_run_t = threading.Thread(target=self._run_loop,name="robot run")
        self.robot_run_t = threading.Thread(target=self.robot.run, name="robot run")
        self.http_server_t = threading.Thread(target=self.http_server.start_web, name="http server")
        self.rbk_connect_t.setDaemon(True)

    def run(self):
        self.rbk_connect_t.start()
        self.mqtt_server.mqtt_client_s.loop_start()
        self.http_server_t.start()
        coroutines = [self.robot.run(), self.robot_order.run(), self.mqtt_server.run()]
        EventLoop.event_loop.run_until_complete(asyncio.gather(*coroutines))

    def _run_loop(self):
        asyncio.set_event_loop(None)
        loop_robot = asyncio.new_event_loop()
        asyncio.set_event_loop(loop_robot)
        loop_robot.run_forever()

    def creat_rbk(self):
        """
        创建一个rbk tcp api 类，用于唯一负责与机器人的通讯
        :return:
        """
        return self.rbk_lib_class(self.config.config.get("robot", "robot_ip"))

    def get_configs(self):
        """
        获取配置文件
        :return:
        """
        return self.config_class()

    def creat_robot(self):
        return self.robot_class(self.rbk)

    def creat_robot_order(self):
        return self.robot_order_class(self.robot,
                                      mode=self.config.config.getint("robot", "mode"),
                                      state_report_frequency=self.config.config.getfloat("network",
                                                                                         "state_report_frequency"),
                                      robot_type=self.config.config.getint("robot", "robot_type"),
                                      script_name=self.config.config.get("script", "script_name"))

    def creat_mqtt_server(self):
        return self.MqttServer_class(**self.config.config_mqtt())

    def creat_http_server(self):
        return self.http_server_class(
            web_host=self.config.config.get("web", "web_host"),
            web_port=self.config.config.getint("web", "web_port"),
            robot_order=self.robot_order,
            robot=self.robot
        )


if __name__ == '__main__':
    app = RoboVda()
    app.run()

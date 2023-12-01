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
    def __init__(self):
        self.config = Config()
        self.rbk = Rbk(self.config.robot_ip)
        self.robot = Robot(self.rbk)
        self.robot_order = HandleTopic(self.robot, self.config)
        self.mqtt_server = MqttServer(self.config)
        self.http_server = HttpServer(
            web_host=self.config.web_host,
            web_port=self.config.web_port,
            robot_order=self.robot_order,
            robot=self.robot)

        self.rbk_run_t = threading.Thread(target=self.rbk.run, name="rbk connect")
        self.robot_run_t = threading.Thread(target=self.robot.run, name="robot run")
        self.http_server_t = threading.Thread(target=self.http_server.run, name="http server")
        set_as_daemon([self.rbk_run_t, self.robot_run_t, self.http_server_t])

    def run(self):
        self.rbk_run_t.start()
        self.http_server_t.start()
        coroutines = [self.robot.run(), self.robot_order.run(), self.mqtt_server.run()]
        EventLoop.event_loop.run_until_complete(asyncio.gather(*coroutines))


def set_as_daemon(threads):
    for thread in threads:
        thread.setDaemon(True)


if __name__ == '__main__':
    app = RoboVda()
    app.run()

import asyncio
import threading
from queue import Queue
import json
import socket
import pydantic
from flask import Flask, render_template, jsonify
from memory_profiler import profile
from paho.mqtt import client as mqtt_client
from type import state, order, instantActions, connection, visualization
from typing import Union
import time
from serve import handle_topic
from log.log import MyLogger

RobotMessage = Union[state.State, str, bytes, order.Order, instantActions.InstantActions, connection.Connection]


class RobotServer:
    def __init__(self, mqtt_host="127.0.0.1",
                 mqtt_port=1883,
                 mqtt_transport="tcp",
                 robot_ip="127.0.0.1",
                 logg=None,
                 mode: int = 0,
                 web_host="127.0.0.1",
                 web_port=5000,
                 mqtt_topic_order: str = None,
                 mqtt_topic_state: str = None,
                 mqtt_topic_visualization: str = None,
                 mqtt_topic_connection: str = None,
                 mqtt_topic_instantActions: str = None,
                 mqtt_topic_factsheet: str = None,
                 state_report_frequency = 1
                 ):
        self.connected = False
        self.logs = logg
        self._event_loop = asyncio.get_event_loop()
        # topic route
        self.mqtt_topic_order = mqtt_topic_order
        self.mqtt_topic_state = mqtt_topic_state
        self.mqtt_topic_visualization = mqtt_topic_visualization
        self.mqtt_topic_connection = mqtt_topic_connection
        self.mqtt_topic_instantActions = mqtt_topic_instantActions
        self.mqtt_topic_factsheet = mqtt_topic_factsheet
        # connect to MQTT
        self._mqtt_client = self._connect_to_mqtt(mqtt_host, mqtt_port, mqtt_transport)
        self._mqtt_messages: asyncio.Queue[RobotMessage] = asyncio.Queue()
        self.robot_order: handle_topic.RobotOrder = handle_topic.RobotOrder(logs=logg, mode=mode,state_report_frequency=state_report_frequency)

        self.mode = mode

        # 创建Flask应用
        self.app = Flask(__name__)
        self.web_host = web_host
        self.web_port = web_port
        # 添加路由
        self._add_routes()
        self.logs.info("init done")

    def _add_routes(self):
        @self.app.route('/')
        def index():
            current_order = self.robot_order.current_order
            current_order_state = self.robot_order.current_order_state
            return render_template('index.html', current_order=current_order, current_order_state=current_order_state)

        @self.app.route('/get_data', methods=['GET'])
        def get_data():
            order1 = None
            if self.robot_order.current_order:
                order1 = json.dumps(self.robot_order.current_order.dict())
            # 这里需要根据具体情况编写逻辑，在此给出一个示例
            data = {
                'current_order': order1,
                'current_order_state': json.dumps(self.robot_order.current_order_state.model_dump())
            }
            return jsonify(data)

        @self.app.route('/getOrderStatus', methods=['GET'])
        def getOrderStatus():
            OrderStatus=self.robot_order.order_state_machine.orders.orders.model_dump()
            if OrderStatus:
                return jsonify(OrderStatus)
            else:
                return jsonify({"code":201,"msg":"没有订单"})

        @self.app.route('/getState', methods=['GET'])
        def getState():
            state = self.robot_order.robot.state.model_dump()
            return jsonify(state)

        @self.app.route('/getPackTask', methods=['GET'])
        def getPackTask():
            PackTask = {
                "task_pack_list":self.robot_order.pack_task.task_pack_list,
                "pack_mode":self.robot_order.pack_task.pack_mode,
                "nodes_point":self.robot_order.pack_task.nodes_point
            }
            return jsonify(PackTask)

    def start_web(self):
        # 启动Flask应用
        self.app.run(host=self.web_host, port=self.web_port)

    def run(self):
        self._mqtt_client.loop_start()
        web_thread = threading.Thread(target=self.start_web)
        web_thread.setDaemon(True)
        web_thread.start()

        self._event_loop.run_until_complete(self._run())

    async def _run(self):
        await asyncio.gather(
            self._handle_mqtt_subscribe_messages(),
            self._handle_mqtt_publish_messages(),
            self._handle_mqtt_publish_messages_connection(),
            self._handle_mqtt_publish_messages_visualization(),
            self._robot_run()
        )

    async def _handle_mqtt_subscribe_messages(self):
        """
        从订阅消息队列里拿数据，执行业务逻辑
        :return:
        """
        while True:
            message = await self._mqtt_messages.get()
            if isinstance(message, state.State):
                self.logs.info(f"[subscribe][{self.mqtt_topic_state}]|{len(message.dict())}|{message.model_dump()}")
            elif isinstance(message, order.Order):
                self.logs.info(f"[subscribe][{self.mqtt_topic_order}]|{len(message.dict())}|{message.model_dump()}")
                self._mqtt_handle_order(message)
            elif isinstance(message, instantActions.InstantActions):
                self.logs.info(f"[subscribe][{self.mqtt_topic_instantActions}]|"
                               f"{len(message.model_dump())}|{message.model_dump()}")
                self._mqtt_handle_instantActions(message)
            elif isinstance(message, connection.Connection):
                self.logs.info(f"[subscribe][{self.mqtt_topic_connection}]|"
                               f"{len(message.model_dump())}|{message.model_dump()}")
                self._mqtt_handle_Connection(message)
            elif isinstance(message, visualization.Visualization):
                self._mqtt_handle_visualization(message)
            else:
                self.logs.info(f"[subscribe][unknown]|{len(message.model_dump())}|{message.model_dump()}")

    async def _handle_mqtt_publish_messages(self):
        """
        发布 机器人状态
        :return:
        """
        while True:
            message = await self.get_state()
            self._mqtt_client.publish(self.mqtt_topic_state, json.dumps(message.model_dump()))
            self.logs.info(f"[publish][{self.mqtt_topic_state}]|"
                           f"{len(json.dumps(message.model_dump()))}")

    async def _handle_mqtt_publish_messages_connection(self):
        """
        online
        :return:
        """
        while True:
            message = await self.get_connection()
            self._mqtt_client.publish(self.mqtt_topic_connection, json.dumps(message.model_dump()))
            self.logs.info(f"[publish][{self.mqtt_topic_connection}]|"
                           f"{len(json.dumps(message.model_dump()))}|{json.dumps(message.model_dump())}")

    async def _handle_mqtt_publish_messages_visualization(self):
        """
        visualization
        :return:
        """
        while True:
            message = await self.get_visualization()
            self._mqtt_client.publish(self.mqtt_topic_visualization, json.dumps(message.model_dump()))
            self.logs.info(f"[publish][{self.mqtt_topic_visualization}]|"
                           f"{len(json.dumps(message.model_dump()))}|")

    async def get_state(self) -> state.State:
        return await self.robot_order.p_state.get()

    async def get_connection(self) -> connection.Connection:
        return await self.robot_order.p_connection.get()

    async def get_visualization(self) -> visualization.Visualization:
        return await self.robot_order.p_visualization.get()

    async def _robot_run(self):
        await self.robot_order.run()

    def _connect_to_mqtt(self, host: str, port: int, transport: str) -> mqtt_client.Client:
        client = mqtt_client.Client(transport=transport)
        client.on_connect = self._mqtt_on_connect
        client.on_message = self._mqtt_on_message
        client.on_disconnect = self._mqtt_on_disconnect
        while not self.connected:
            try:
                client.connect(host, port)
                self.connected = True
                self.logs.info("MQTT blocker connect finnish")
            except ConnectionRefusedError:
                self.logs.error("MQTT blocker Failed to connect to mqtt broker, retrying in 1 s")
                time.sleep(1)
            except socket.gaierror:
                self.logs.error(f"Could not resolve mqtt hostname {host}, retrying in ")
                time.sleep(1)
            except socket.timeout as e:
                self.logs.error(f"Could not resolve mqtt hostname {host}, socket.timeout {e} ")
                time.sleep(1)
            except OSError as o:
                self.logs.error(f"Could not resolve mqtt hostname {host}, socket.timeout {o} ")
                time.sleep(1)
        return client

    def _mqtt_on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.mqtt_topic_order)
        client.subscribe(self.mqtt_topic_state)
        client.subscribe(self.mqtt_topic_connection)
        client.subscribe(self.mqtt_topic_factsheet)
        client.subscribe(self.mqtt_topic_instantActions)
        client.subscribe(self.mqtt_topic_visualization)
        self.logs.info(f"serve subscribe start:{self.mqtt_topic_order}|{self.mqtt_topic_state}|"
                       f"{self.mqtt_topic_connection}|{self.mqtt_topic_factsheet}|{self.mqtt_topic_instantActions}|"
                       f"{self.mqtt_topic_visualization}|")

    def _mqtt_on_message(self, client, userdata, msg):
        try:
            self.logs.info(f"[MQTT] recv:{msg}")
            if msg.topic == self.mqtt_topic_state:
                self.logs.info(f"topic {self.mqtt_topic_state} rec")
                self._enqueue(state.State(**json.loads(msg.payload)))
            elif msg.topic == self.mqtt_topic_order:
                self.logs.info(f"topic {self.mqtt_topic_order} rec")
                self._enqueue(order.Order(**json.loads(msg.payload)))
            elif msg.topic == self.mqtt_topic_instantActions:
                self.logs.info(f"topic {self.mqtt_topic_instantActions} rec")
                self._enqueue(instantActions.InstantActions(**json.loads(msg.payload)))
            elif msg.topic == self.mqtt_topic_connection:
                self.logs.info(f"topic {self.mqtt_topic_connection} rec")
                self._enqueue(connection.Connection(**json.loads(msg.payload)))
            elif msg.topic == self.mqtt_topic_visualization:
                self.logs.info(f"topic {self.mqtt_topic_connection} rec")
                self._enqueue(visualization.Visualization(**json.loads(msg.payload)))
            else:
                self.logs.info("未知消息", msg.payload)
        except pydantic.error_wrappers.ValidationError as e:
            # 在这里处理ValidationError异常
            # 可以打印出错误消息或执行其他逻辑
            self.logs.error(f"Validation Error:{e}")

    def _mqtt_on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.logs.error(f"[MQTT]mqtt Disconnected:{rc}")

    def _enqueue(self, obj):
        asyncio.run_coroutine_threadsafe(self._mqtt_messages.put(obj), self._event_loop)

    def _mqtt_handle_order(self, sub_order: order.Order):
        asyncio.run_coroutine_threadsafe(self.robot_order.s_order.put(sub_order), self._event_loop)
        self.logs.info(f"MQTT 订单队列大小：{self.robot_order.s_order.qsize()}")

    def _mqtt_handle_instantActions(self, instant: instantActions.InstantActions):
        self.robot_order.handle_instantActions(instant)

    def _mqtt_handle_Connection(self, message):
        self.logs.info(f"_mqtt_handle_Connection ,message len:{message.model_dump().__len__()} ")

    def _mqtt_handle_visualization(self, message):
        self.logs.info(f"[subscribe][{self.mqtt_topic_visualization}]|"
                       f"{len(message.model_dump())}|")

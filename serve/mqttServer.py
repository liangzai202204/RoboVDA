import asyncio
import json
import socket
import time
from typing import Union
import pydantic
from paho.mqtt import client as mqtt_client
from log.log import MyLogger
from serve.topicQueue import TopicQueue, EventLoop
from type import state, order, instantActions, connection, visualization, factsheet

RobotMessage = Union[state.State, str, bytes, order.Order, instantActions.InstantActions, connection.Connection]


class MqttServer:
    def __init__(self,
                 mqtt_host="127.0.0.1",
                 mqtt_port=1883,
                 mqtt_transport="tcp",
                 mqtt_topic_order: str = None,
                 mqtt_topic_state: str = None,
                 mqtt_topic_visualization: str = None,
                 mqtt_topic_connection: str = None,
                 mqtt_topic_instantActions: str = None,
                 mqtt_topic_factsheet: str = None,
                 ):
        self.connected = False
        self.logs = MyLogger()
        # topic route
        self.mqtt_topic_order = mqtt_topic_order
        self.mqtt_topic_state = mqtt_topic_state
        self.mqtt_topic_visualization = mqtt_topic_visualization
        self.mqtt_topic_connection = mqtt_topic_connection
        self.mqtt_topic_instantActions = mqtt_topic_instantActions
        self.mqtt_topic_factsheet = mqtt_topic_factsheet
        # connect to MQTT
        print("-----", mqtt_host, mqtt_port, mqtt_transport)
        self.mqtt_client_s = self._connect_to_mqtt(mqtt_host, mqtt_port, mqtt_transport)
        self._mqtt_messages: asyncio.Queue[RobotMessage] = asyncio.Queue()

    async def run(self):
        await asyncio.gather(
            self._handle_mqtt_subscribe_messages(),
            self._handle_mqtt_publish_messages(),
            self._handle_mqtt_publish_messages_connection(),
            self._handle_mqtt_publish_messages_visualization()
        )

    async def _handle_mqtt_subscribe_messages(self):
        """
        从订阅消息队列里拿数据，执行业务逻辑
        :return:
        """
        while True:
            message = await self._mqtt_messages.get()
            if isinstance(message, state.State):
                # self.logs.info(f"[subscribe]"
                #                f"[{self.mqtt_topic_state}]|"
                #                f"{len(message.model_dump())}|{message.model_dump().__len__()}")
                pass
            elif isinstance(message, order.Order):
                self.logs.info(f"[subscribe][{self.mqtt_topic_order}]|"
                               f"{len(message.model_dump())}|{message.model_dump()}")
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
            self.mqtt_client_s.publish(self.mqtt_topic_state, json.dumps(message.model_dump()))
            self.logs.info(f"[publish][{self.mqtt_topic_state}]|"
                           f"{len(json.dumps(message.model_dump()))}")

    async def _handle_mqtt_publish_messages_connection(self):
        """
        online
        :return:
        """
        while True:
            message = await self.get_connection()
            self.mqtt_client_s.publish(self.mqtt_topic_connection, json.dumps(message.model_dump()))
            self.logs.info(f"[publish][{self.mqtt_topic_connection}]|"
                           f"{len(json.dumps(message.model_dump()))}|{json.dumps(message.model_dump())}")

    async def _handle_mqtt_publish_messages_visualization(self):
        """
        visualization
        :return:
        """
        while True:
            message = await self.get_visualization()
            self.mqtt_client_s.publish(self.mqtt_topic_visualization, json.dumps(message.model_dump()))
            self.logs.info(f"[publish][{self.mqtt_topic_visualization}]|"
                           f"{len(json.dumps(message.model_dump()))}|")

    async def get_state(self) -> state.State:
        return await TopicQueue.p_state.get()

    async def get_connection(self) -> connection.Connection:
        return await TopicQueue.p_connection.get()

    async def get_visualization(self) -> visualization.Visualization:
        return await TopicQueue.p_visualization.get()

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
        self.logs.info(f"serve subscribe start:"
                       f"{self.mqtt_topic_order}|"
                       f"{self.mqtt_topic_state}|"
                       f"{self.mqtt_topic_connection}|"
                       f"{self.mqtt_topic_factsheet}|"
                       f"{self.mqtt_topic_instantActions}|"
                       f"{self.mqtt_topic_visualization}|")

    def _mqtt_on_message(self, client, userdata, msg):
        try:
            # self.logs.info(f"[MQTT] recv:{msg}")
            if msg.topic == self.mqtt_topic_state:
                # self.logs.info(f"topic {self.mqtt_topic_state} rec")
                # self._enqueue(state.State(**json.loads(msg.payload)))
                pass
            elif msg.topic == self.mqtt_topic_order:
                self.logs.info(f"topic {self.mqtt_topic_order} rec,CONTENT:{msg.payload}")
                self._enqueue(order.Order(**json.loads(msg.payload)))
            elif msg.topic == self.mqtt_topic_instantActions:
                self.logs.info(f"topic {self.mqtt_topic_instantActions} rec")
                self._enqueue(instantActions.InstantActions(**json.loads(msg.payload)))
            elif msg.topic == self.mqtt_topic_connection:
                self.logs.info(f"topic {self.mqtt_topic_connection} rec")
                self._enqueue(connection.Connection(**json.loads(msg.payload)))
            elif msg.topic == self.mqtt_topic_visualization:
                self.logs.info(f"topic {self.mqtt_topic_visualization} rec")
                self._enqueue(visualization.Visualization(**json.loads(msg.payload)))
            elif msg.topic == self.mqtt_topic_factsheet:
                self.logs.info(f"topic {self.mqtt_topic_factsheet} rec")
                self._enqueue(factsheet.Factsheet(**json.loads(msg.payload)))
            else:
                self.logs.info(f"未知消息{msg.payload}")
        except pydantic.error_wrappers.ValidationError as e:
            # 在这里处理ValidationError异常
            # 可以打印出错误消息或执行其他逻辑
            self.logs.error(f"Validation Error:{e}")

    def _mqtt_on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.logs.error(f"[MQTT]mqtt Disconnected:{rc}")

    def _enqueue(self, obj):
        asyncio.run_coroutine_threadsafe(self._mqtt_messages.put(obj), EventLoop.event_loop)

    def _mqtt_handle_order(self, sub_order: order.Order):
        asyncio.run_coroutine_threadsafe(TopicQueue.s_order.put(sub_order), EventLoop.event_loop)
        self.logs.info(f"MQTT s_order 订单队列大小：{TopicQueue.s_order.qsize()}")

    def _mqtt_handle_instantActions(self, instant: instantActions.InstantActions):
        asyncio.run_coroutine_threadsafe(TopicQueue.s_instantActions.put(instant), EventLoop.event_loop)
        self.logs.info(f"MQTT s_instantActions 订单队列大小：{TopicQueue.s_instantActions.qsize()}")

    def _mqtt_handle_Connection(self, message):
        self.logs.info(f"_mqtt_handle_Connection ,message len:{message.model_dump().__len__()} ")

    def _mqtt_handle_visualization(self, message):
        self.logs.info(f"[subscribe][{self.mqtt_topic_visualization}]|"
                       f"{len(message.model_dump())}|")

    def _mqtt_handle_fact_sheet(self, factSheet: factsheet.Factsheet):
        asyncio.run_coroutine_threadsafe(TopicQueue.s_factSheet.put(factSheet), EventLoop.event_loop)
        self.logs.info(f"MQTT s_factSheet 订单队列大小：{TopicQueue.s_factSheet.qsize()}")

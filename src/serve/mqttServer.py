import asyncio
import json
import socket
import time
from typing import Union
from paho.mqtt import client as mqtt_client
from src.log.log import MyLogger
from src.serve.topicQueue import TopicQueue, EventLoop
from src.type.VDA5050 import state, order, factsheet, connection, instantActions, visualization
from src.config.config import Config

RobotMessage = Union[state.State, str, bytes, order.Order, instantActions.InstantActions, connection.Connection]


class MqttServer:
    def __init__(self, config: Config):
        self.connected = False
        self.logs = MyLogger()
        self.config = config
        # connect to MQTT
        print("mqtt connection", config.mqtt_host, config.mqtt_port, config.mqtt_transport)
        self.mqtt_client_s = None
        self._mqtt_messages: asyncio.Queue[RobotMessage] = asyncio.Queue()
        self.msg_topics = {
            self.config.mqtt_topic_state: state.State,
            self.config.mqtt_topic_order: order.Order,
            self.config.mqtt_topic_instantActions: instantActions.InstantActions,
            self.config.mqtt_topic_connection: connection.Connection,
            self.config.mqtt_topic_visualization: visualization.Visualization,
            self.config.mqtt_topic_factsheet: factsheet.FactSheet
        }
        self.handlers = {
            state.State: self._mqtt_handle_state,
            order.Order: self._mqtt_handle_order,
            instantActions.InstantActions: self._mqtt_handle_instantActions,
            connection.Connection: self._mqtt_handle_Connection,
            visualization.Visualization: self._mqtt_handle_visualization,
            factsheet.FactSheet: self._mqtt_handle_fact_sheet
        }

    async def run(self):
        while True:
            if not self.connected or not self.mqtt_client_s:
                self.mqtt_client_s = self._connect_to_mqtt(self.config.mqtt_host,
                                                           self.config.mqtt_port,
                                                           self.config.mqtt_transport)
                if self.mqtt_client_s and self.connected:
                    self.mqtt_client_s.loop_start()
                    self.logs.info(f"[MQTT]MQTT online")
                else:
                    self.logs.info(f"[MQTT]MQTT not online ,waiting 10 s")
                await asyncio.sleep(1)

            else:
                await self._run()

    async def _run(self):
        results = await asyncio.gather(
            self._handle_mqtt_subscribe_messages(),
            self._handle_mqtt_publish_messages_sate(),
            self._handle_mqtt_publish_messages_connection(),
            self._handle_mqtt_publish_messages_visualization()
        )
        # 所有协程执行完毕后的回调函数
        self.logs.info(f"[mqtt]All coroutines have finished executing!{results}")

    async def _handle_mqtt_subscribe_messages(self):
        """
        从订阅消息队列里拿数据，执行业务逻辑
        :return:
        """
        while True:
            if not self.mqtt_client_s:
                self.mqtt_client_s = self._connect_to_mqtt(self.config.mqtt_host,
                                                           self.config.mqtt_port,
                                                           self.config.mqtt_transport)
            message = await self._mqtt_messages.get()
            if handler := self.handlers.get(type(message)):
                handler(message)
            else:
                self.logs.info(f"[subscribe][unknown]|{len(message.model_dump())}|{message.model_dump()}")

    async def _handle_mqtt_publish_messages_sate(self):
        """
        发布 机器人状态
        :return:
        """
        while True:
            message = await self.get_state()
            self.mqtt_client_s.publish(self.config.mqtt_topic_state, json.dumps(message.model_dump()))
            # self.logs.info(f"[publish][{self.mqtt_topic_state}]|"
            #                f"{len(json.dumps(message.model_dump()))}")

    async def _handle_mqtt_publish_messages_connection(self):
        """
        online
        :return:
        """
        while True:
            message = await self.get_connection()
            self.mqtt_client_s.publish(self.config.mqtt_topic_connection, json.dumps(message.model_dump()))
            # self.logs.info(f"[publish][{self.mqtt_topic_connection}]|"
            #                f"{len(json.dumps(message.model_dump()))}|{json.dumps(message.model_dump())}")

    async def _handle_mqtt_publish_messages_visualization(self):
        """
        visualization
        :return:
        """
        while True:
            message = await self.get_visualization()
            self.mqtt_client_s.publish(self.config.mqtt_topic_visualization, json.dumps(message.model_dump()))
            # self.logs.info(f"[publish][{self.mqtt_topic_visualization}]|"
            #                f"{len(json.dumps(message.model_dump()))}|")

    async def get_state(self) -> state.State:
        return await TopicQueue.p_state.get()

    async def get_connection(self) -> connection.Connection:
        return await TopicQueue.p_connection.get()

    async def get_visualization(self) -> visualization.Visualization:
        return await TopicQueue.p_visualization.get()

    def _connect_to_mqtt(self, host: str, port: int, transport: str) -> mqtt_client.Client:
        client = mqtt_client.Client(transport=transport)
        offline = """
                {
                    "connectionState": "CONNECTIONBROKEN",
                    "headerId": 999999999,
                    "manufacturer": "seer",
                    "serialNumber": "",
                    "timeStamp": "2023-02-06T16:40:01.474Z",
                    "version": "5.0.0"
                }"""
        client.will_set(self.config.mqtt_topic_connection, payload=offline, qos=1, retain=True)
        client.on_connect = self._mqtt_on_connect
        client.on_message = self._mqtt_on_message
        client.on_disconnect = self._mqtt_on_disconnect
        try:
            client.connect(host, port)
            self.connected = True
            self.logs.info("MQTT blocker connect finnish")
            return client
        except ConnectionRefusedError:
            self.logs.error("MQTT blocker Failed to connect to mqtt broker, retrying in 1 s")
        except socket.gaierror:
            self.logs.error(f"Could not resolve mqtt hostname {host}, retrying in ")
        except socket.timeout as e:
            self.logs.error(f"Could not resolve mqtt hostname {host}, socket.timeout {e} ")
        except OSError as o:
            self.logs.error(f"Could not resolve mqtt hostname {host}, socket.timeout {o} ")
        self.connected = False
        return None

    def _mqtt_on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.config.mqtt_topic_order)
        client.subscribe(self.config.mqtt_topic_state)
        client.subscribe(self.config.mqtt_topic_connection)
        client.subscribe(self.config.mqtt_topic_factsheet)
        client.subscribe(self.config.mqtt_topic_instantActions)
        client.subscribe(self.config.mqtt_topic_visualization)
        self.logs.info(f"serve subscribe start:"
                       f"{self.config.mqtt_topic_order}|"
                       f"{self.config.mqtt_topic_state}|"
                       f"{self.config.mqtt_topic_connection}|"
                       f"{self.config.mqtt_topic_factsheet}|"
                       f"{self.config.mqtt_topic_instantActions}|"
                       f"{self.config.mqtt_topic_visualization}|")

    def _mqtt_on_message(self, client, userdata, msg):
        try:

            if topic_class := self.msg_topics.get(msg.topic):
                if msg.topic == self.config.mqtt_topic_order or self.config.mqtt_topic_instantActions == msg.topic:
                    self.logs.info(f"[mqtt]topic {msg.topic} rec")
                    self.logs.info(f"[mqtt]topic {msg.topic}||{msg.payload}")
                self._enqueue(topic_class(**json.loads(msg.payload)))
            else:
                self.logs.info(f"[mqtt]未知消息{msg.payload}")
        except Exception as e:
            self.logs.error(f"[MQTT]recv Exception Error:{e}")

    def _mqtt_on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.mqtt_client_s = None
        self.mqtt_client_s = self._connect_to_mqtt(self.config.mqtt_host,
                                                   self.config.mqtt_port,
                                                   self.config.mqtt_transport)
        self.logs.error(f"[MQTT]mqtt Disconnected:{rc}")

    def _enqueue(self, obj):
        asyncio.run_coroutine_threadsafe(self._mqtt_messages.put(obj), EventLoop.event_loop)

    def _mqtt_handle_state(self, state: state.State):
        # self.logs.info(state.model_dump())
        pass

    def _mqtt_handle_order(self, sub_order: order.Order):
        asyncio.run_coroutine_threadsafe(TopicQueue.s_order.put(sub_order), EventLoop.event_loop)
        self.logs.info(f"MQTT s_order 订单队列大小：{TopicQueue.s_order.qsize()}")

    def _mqtt_handle_instantActions(self, instant: instantActions.InstantActions):
        asyncio.run_coroutine_threadsafe(TopicQueue.s_instantActions.put(instant), EventLoop.event_loop)
        self.logs.info(f"MQTT s_instantActions 订单队列大小：{TopicQueue.s_instantActions.qsize()}")

    def _mqtt_handle_Connection(self, message):
        # self.logs.info(f"_mqtt_handle_Connection ,message len:{message.model_dump().__len__()} ")
        pass

    def _mqtt_handle_visualization(self, message):
        # self.logs.info(f"[subscribe][{self.mqtt_topic_visualization}]|"
        #                f"{len(message.model_dump())}|")
        pass

    def _mqtt_handle_fact_sheet(self, factSheet: factsheet.FactSheet):
        asyncio.run_coroutine_threadsafe(TopicQueue.s_factSheet.put(factSheet), EventLoop.event_loop)
        self.logs.info(f"MQTT s_factSheet 订单队列大小：{TopicQueue.s_factSheet.qsize()}")

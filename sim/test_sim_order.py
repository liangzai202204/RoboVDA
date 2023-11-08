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


    def test_straight(self):
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")
        json_filename = 'Transport Order 3066 straight.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
        client = mqtt.Client()
        client.connect(get_mqtt_ip(), 1883, 60)
        client.publish(get_order_topic(), json.dumps(json_content))
        print("ok")

    def test_creat_order_87(self):
        import json
        import sim_order as s
        a = s.SimOrder(ip="192.168.198.168")
        datas = []
        par = [
                        {
                            "key": "height",
                            "value": "0.1"
                        },
                        {
                            "key": "depth",
                            "value": "0.9"
                        },
                        {
                            "key": "loadId",
                            "value": "21"
                        }
                    ]
        data = ("LM87", par)
        datas.append(data)
        o1 = a.creat_order(datas, released=True, order_count=100,init="LM87",action_type="test")
        client = mqtt.Client()
        client.connect(get_mqtt_ip(), 1883, 60)

        for o in o1:
            client.publish(get_order_topic(), json.dumps(o.model_dump()))
            print("---", json.dumps(o.model_dump()))
            time.sleep(2)
        print(len(o1))

    def test_order_binTask_empty_params(self):
        import json
        import sim_order as s
        a = s.SimOrder(ip="192.168.198.168")
        datas = []
        params = [{
            "key": "id",
            "value": "loc-1"
        }, {
            "key": "binTask",
            "value": "load"
        }]
        data1 = ("AP105", params)
        data2 = ("LM96", [])
        data3 = ("AP105", params)
        datas.append(data1)
        datas.append(data2)
        datas.append(data3)
        o1 = a.creat_order(datas, released=True, order_count=10)
        client = mqtt.Client()
        client.connect(get_mqtt_ip(), 1883, 60)

        for o in o1:
            client.publish(get_order_topic(), json.dumps(o.model_dump()))
            print("---", json.dumps(o.model_dump()))
            time.sleep(1)
        print(len(o1))

    def assertEqual_relased(self, o1, o2):
        self.assertNotEqual(len(o1.nodes), len(o2.nodes))
        c_o1 = 0
        c_o2 = 0
        for n1 in o1.nodes:
            if n1.released:
                c_o1 += 1
        for n2 in o2.nodes:
            if n2.released:
                c_o2 += 1
        self.assertEqual(c_o1 + c_o2, len(o1.nodes))

        c_o1 = 0
        c_o2 = 0
        for e1 in o1.edges:
            if e1.released:
                c_o1 += 1
        for e2 in o2.edges:
            if e2.released:
                c_o2 += 1
        self.assertEqual(c_o1 + c_o2, len(o1.edges))

    def test_order_binTask_single_params(self):
        import json
        import sim_order as s
        import paho.mqtt.client as mqtt

        a = s.SimOrder(ip="192.168.198.168")
        datas = []
        params = [{
            "key": "id",
            "value": "loc-1"
        }, {
            "key": "binTask",
            "value": "load"
        }]
        data1 = ("AP105", params)
        # data2 = ("LM96", [])
        # data3 = ("AP105", params)
        datas.append(data1)
        # datas.append(data2)
        # datas.append(data3)
        o1, o2 = a.creat_order(datas, released=False)
        print("---", json.dumps(o1.dict()))
        print("===", json.dumps(o2.dict()))
        client = mqtt.Client()

        def mqtt_on_connect(c, userdata, flags, rc):
            c.subscribe("robot/state")

        def mqtt_on_message(c, userdata, msg):
            if msg.topic == "robot/state":
                print("-------")
                state_o = state.State(**json.loads(msg.payload))
                print(state_o.dict())
                if state_o and isinstance(state_o, state.State):
                    n = False
                    e = False
                    print("检查", len(state_o.edgeStates), len(state_o.nodeStates))
                    for ee in state_o.edgeStates:
                        if ee.released:
                            e = True
                    for nn in state_o.nodeStates:
                        if nn.released:
                            n = True

                    if not e and not n:
                        if state_o.orderId == o1.orderId:
                            client.publish("robot/order", json.dumps(o2.dict()))
                            client.disconnect()

        client.on_connect = mqtt_on_connect
        client.on_message = mqtt_on_message
        client.connect("127.0.0.1", 1883, 60)

        client.publish("robot/order", json.dumps(o1.dict()))
        client.loop_forever()


class InstantActionsTest(unittest.TestCase):

    def test_straight(self):
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")
        json_filename = 'test_straight.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
        client = mqtt.Client()
        client.connect(get_mqtt_ip(), 1883, 60)
        print(json.dumps(json_content))
        client.publish("robot/order", json.dumps(json_content))

    def test_instantActions_cancelOrder(self):
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")
        json_filename = 'Cancel Order InstantAction.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
        client = mqtt.Client()
        client.connect(get_mqtt_ip(), 1883, 60)
        print(json.dumps(json_content))
        client.publish("robot/instantActions", json.dumps(json_content))

    def test_instantActions_startPause(self):
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")

        json_filename = 'startPaues Order InstantAction.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
        client = mqtt.Client()
        client.connect(get_mqtt_ip(), 1883, 60)
        client.publish("robot/instantActions", json.dumps(json_content))

    def test_instantActions_stopPause(self):
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")

        json_filename = 'stopPaues Order InstantAction.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
        client = mqtt.Client()
        client.connect(get_mqtt_ip(), 1883, 60)
        client.publish("robot/instantActions", json.dumps(json_content))

    def test_OOO(self):
        from serve import OrderStateMachine
        # # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        # path_to_B = os.path.abspath("../VDAExample")
        # json_filename = 'Transport Order.json'
        #
        # json_file_path = os.path.join(path_to_B, json_filename)
        #
        # with open(json_file_path, 'r') as json_file:
        #     json_content = json.load(json_file)
        #     #print(json_content)
        a=OrderStateMachine.OrderStateMachine()
        print(a.orders.orders.orderId)
        # a.init_order(order.Order(**json_content))
        # a.orders.orders.set_node_status_by_id("7a434ec3-91c8-4334-89f8-31d30942fbb7",OrderStateMachine.Status.FINISHED)
        # n = a.orders.orders.get_status_by_id("7a434ec3-91c8-4334-89f8-31d30942fbb7")

    def test_pack_class(self):
        import json
        import os
        from serve.packTask import PackTask
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")
        json_filename = 'Transport Order.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
        p=PackTask(2,{})
        a= order.Order(**json_content)
        t=p.pack(a)
        print(t)

    def test_a(self):
        import asyncio

        async def handle_client(reader, writer):
            # 处理客户端连接的逻辑
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                print(f"Received data from client: {data.decode()}")
                writer.write(data)
                await writer.drain()

            writer.close()

        async def start_server(host, port):
            server = await asyncio.start_server(handle_client, host, port)
            print(f"Server started on {host}:{port}")

            async with server:
                await server.serve_forever()

        async def main():
            host = 'localhost'
            port = 1234
            await start_server(host, port)

        asyncio.run(main())


if __name__ == '__main__':
    # unittest.main()
    print(182323-67996)
    print((182323-67996)/1000)

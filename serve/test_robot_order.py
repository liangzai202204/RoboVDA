import asyncio
import unittest
import uuid
import json
import uuid
import paho.mqtt.client as mqtt
from serve.handle_topic import RobotOrder, RobotOrderStatus
from type import order
from log.log import MyLogger


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_node(self):
        data = {
            "nodes": [
                {
                    "nodeId": "node-1",
                    "sequenceId": 0,
                    "nodeDescription": "Device initial position",
                    "released": True
                },
                {
                    "nodeId": "node-2",
                    "sequenceId": 2,
                    "nodeDescription": "Device initial position",
                    "released": True
                },
                {
                    "nodeId": "node-3",
                    "sequenceId": 4,
                    "nodeDescription": "Device initial position",
                    "released": False
                }
            ],
            "edges": [
                {
                    "edgeId": "758de28a-c7f6-4475-b623-c4c895780b26",
                    "sequenceId": 1,
                    "released": True,
                    "startNodeId": "node-1",
                    "endNodeId": "node-2"
                },
                {
                    "edgeId": "758de28a-c7f6-4475-b623-c4c895780b26",
                    "sequenceId": 3,
                    "released": False,
                    "startNodeId": "node-2",
                    "endNodeId": "node-3"
                }
            ]
        }

        # 检查 nodes 和 edges 是否为列表，并且是否存在
        if not isinstance(data.get('nodes'), list) or not isinstance(data.get('edges'), list):
            print("Data format error!")
            exit()
        if (len(data["nodes"]) - 1) != len(data["edges"]):
            print("nodes len edges len")
        nodes = [node for node in data['nodes'] if node.get('released', False)]
        edges = [edge for edge in data['edges'] if edge.get('released', False)]

        # 根据 sequenceId 排序 nodes 和 edges
        nodes.sort(key=lambda x: x['sequenceId'])
        edges.sort(key=lambda x: x['sequenceId'])

        # 将 nodes 和 edges 按照要求交替放入 result 中
        result = []

        # 使用双指针进行交替插入
        i, j = 0, 0
        while i < len(nodes) and j < len(edges):
            if edges[j]['startNodeId'] != nodes[i]['nodeId'] and edges[j]['endNodeId'] != nodes[i + 1]['nodeId']:
                print("Data format error!")
                exit()
            result.append(nodes[i])
            result.append(edges[j])
            i += 1
            j += 1

        # 将剩余节点或边插入到 result 中
        result.extend(nodes[i:])
        result.extend(edges[j:])

        print(result)


class RobotOrderT(unittest.TestCase):
    def test_order(self):
        r = RobotOrder()
        asyncio.gather(r.report())
        self.assertEqual(True, False)  # add assertion here

    def test_node_sort(self):
        data = {
            "headerId": 1,
            "timestamp": "1234567",
            "version": "2.0.0",
            "manufacturer": "seer",
            "serialNumber": "AMB-01",
            "orderId": "man-20230531",
            "orderUpdateId": 9,
            "nodes": [
                {
                    "nodeId": "LM100",
                    "sequenceId": 2,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM99",
                    "sequenceId": 1,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                }
            ],
            "edges": [
                {
                    "edgeId": "e1",
                    "sequenceId": 0,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                },
                {
                    "edgeId": "e2",
                    "sequenceId": 2,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                }
            ]
        }
        o = order.Order(**data)
        o.nodes.sort(key=lambda x: x.dict()["sequenceId"])
        print(o.nodes)

    def test_packag_tasksV1(self):
        l = MyLogger()
        r = RobotOrder(logs=l)
        # 空 node
        node0 = {}
        # r.packag_tasks([order.Node(**node0)],[])
        # 不含动作的 node
        node1 = {
            "nodeId": "LM99",
            "sequenceId": 1,
            "released": True,
            "actions": [],
            "nodeDescription": ""
        }
        r.pack_tasks([order.Node(**node1)], [])
        # 含动作的 node
        node2 = {
            "nodeId": "LM99",
            "sequenceId": 1,
            "released": True,
            "actions": [
                {
                    "actionType": "pick",
                    "actionId": str(uuid.uuid4()),
                    "blockingType": "HARD",
                    "actionParameters": [
                        {
                            "key": "stationName",
                            "value": "GPC-B-B1"
                        },
                        {
                            "key": "stationType",
                            "value": "ForkLoad"
                        }
                    ],
                    "actionDescription": "pick item"
                }
            ],
            "nodeDescription": ""
        }
        task_list = r.pack_tasks([order.Node(**node2)], [])
        ex = [{'id': 'LM99', 'source_id': 'LM99', 'task_id': 'a798567d-90a7-446e-928c-af9b0f5287b9'},
              {'id': 'GPC-B-B1', 'task_id': '9c1bc143-fb1c-4ee6-9e82-7c979c6545bf', 'binTask': 'ForkLoad'}]
        self.assertEqual(len(ex), len(task_list))
        self.assertEqual(ex[0]["id"], task_list[0]["id"])
        self.assertEqual(ex[1]["binTask"], task_list[1]["binTask"])
        node3 = {
            "nodeId": "LM99",
            "sequenceId": 1,
            "released": True,
            "actions": [
                {
                    "actionType": "pick",
                    "actionId": str(uuid.uuid4()),
                    "blockingType": "HARD",
                    "actionParameters": [
                        {
                            "key": "stationName",
                            "value": "GPC-B-B1"
                        },
                        {
                            "key": "stationType",
                            "value": "ForkLoad"
                        }
                    ],
                    "actionDescription": "pick item"
                },
                {
                    "actionType": "pick",
                    "actionId": "1",
                    "blockingType": "HARD",
                    "actionParameters": [
                        {
                            "key": "lhd",
                            "value": "LHD1"
                        },
                        {
                            "key": "stationType",
                            "value": "Conveyor"
                        },
                        {
                            "key": "stationName",
                            "value": "Conveyor1"
                        },
                        {
                            "key": "loadType",
                            "value": "Box"
                        },
                        {
                            "key": "loadId",
                            "value": "Box1"
                        },
                        {
                            "key": "height",
                            "value": 1.5
                        },
                        {
                            "key": "depth",
                            "value": 1.2
                        },
                        {
                            "key": "side",
                            "value": "Left"
                        }
                    ],
                    "actionDescription": "Pick up a box from the conveyor."
                }
            ],
            "nodeDescription": ""
        }
        task_list3 = r.pack_tasks([order.Node(**node3)], [])
        self.assertEqual(3, len(task_list3))

    def test_pack_nodes_edges_list(self):
        import json
        import os

        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")
        json_filename = 'Transport Order.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
        o = order.Order(**json_content)
        l = MyLogger()
        r = RobotOrder(logs=l)
        l = len(o.nodes) + len(o.edges)
        n = o.nodes
        e = o.edges
        t = r.pack_tasks(n, e)
        print(len(t))
        self.assertEqual(len(t), l)

    def test_pack_task(self):
        import json
        import os

        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")
        json_filename = 'Transport Order.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
        o = order.Order(**json_content)
        l = MyLogger()
        r = RobotOrder(logs=l)

        task = r.pack_tasks(o.nodes, o.edges)
        print("node id:", r.nodes_id_list)
        print("edge id:", r.edges_id_list)
        print("action id:", r.actions_id_list)
        print(r.nodes_state)
        print(r.edges_state)
        print(r.actions_state)

        self.assertEqual(len(o.nodes) + len(o.edges), 13)
        self.assertEqual(len(task), 3)
        self.assertEqual(RobotOrderStatus.Waiting, 1)


class RobotOrderTest(unittest.TestCase):
    def test_order_1_1(self):
        client = mqtt.Client()
        client.connect("127.0.0.1", 1883, 60)
        data = {
            "headerId": 1,
            "timestamp": "1234567",
            "version": "2.0.0",
            "manufacturer": "seer",
            "serialNumber": "AMB-01",
            "orderId": "man-20230531",
            "orderUpdateId": 1,
            "nodes": [
                {
                    "nodeId": "LM99",
                    "sequenceId": 5,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "AP107",
                    "sequenceId": 6,
                    "released": False,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B2"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                }
            ],
            "edges": [
                {
                    "edgeId": "e1",
                    "sequenceId": 0,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                },
                {
                    "edgeId": "e2",
                    "sequenceId": 2,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                }
            ]
        }
        client.publish("robot/order", json.dumps(data))

    def test_order_1_2(self):
        client = mqtt.Client()
        client.connect("127.0.0.1", 1883, 60)
        data = {
            "headerId": 1,
            "timestamp": "1234567",
            "version": "2.0.0",
            "manufacturer": "seer",
            "serialNumber": "AMB-01",
            "orderId": "man-20230531",
            "orderUpdateId": 1,
            "nodes": [
                {
                    "nodeId": "LM99",
                    "sequenceId": 5,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "AP107",
                    "sequenceId": 6,
                    "released": True,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B2"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                }
            ],
            "edges": [
                {
                    "edgeId": "e1",
                    "sequenceId": 0,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                },
                {
                    "edgeId": "e2",
                    "sequenceId": 2,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                }
            ]
        }
        client.publish("robot/order", json.dumps(data))

    def test_order_2_1(self):
        client = mqtt.Client()
        client.connect("127.0.0.1", 1883, 60)
        data = {
            "headerId": 1,
            "timestamp": "1234567",
            "version": "2.0.0",
            "manufacturer": "seer",
            "serialNumber": "AMB-01",
            "orderId": "man-20230531123-3",
            "orderUpdateId": 3,
            "nodes": [
                {
                    "nodeId": "LM99",
                    "sequenceId": 1,
                    "released": True,
                    "actions": [],
                    "nodeDescription": "",
                    "nodePosition": {
                        "x": -18.077,
                        "y": -2.104,
                        "theta": -0.026340157,
                        "allowedDeviationXY": 0.5,
                        "allowedDeviationTheta": 0.5,
                        "mapId": "01632ba1-5e0f-41b3-9d1c-b701fa168c3f",
                        "mapDescription": "Id: 01632ba1-5e0f-41b3-9d1c-b701fa168c3f"
                    }
                },
                {
                    "nodeId": "LM98",
                    "sequenceId": 2,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM97",
                    "sequenceId": 3,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "AP105",
                    "sequenceId": 4,
                    "released": True,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B4"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM97",
                    "sequenceId": 5,
                    "released": False,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM96",
                    "sequenceId": 6,
                    "released": False,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "AP104",
                    "sequenceId": 7,
                    "released": False,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B5"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                },
            ],
            "edges": [
                {
                    "edgeId": "e1",
                    "sequenceId": 0,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "maxSpeed": None,
                    "maxHeight": None,
                    "minHeight": None,
                    "orientation": None,
                    "direction": None,
                    "rotationAllowed": None,
                    "maxRotationSpeed": None,
                    "trajectory": None,
                    "length": None,
                    "actions": []
                },
                {
                    "edgeId": "e2",
                    "sequenceId": 2,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "maxSpeed": None,
                    "maxHeight": None,
                    "minHeight": None,
                    "orientation": None,
                    "direction": None,
                    "rotationAllowed": None,
                    "maxRotationSpeed": None,
                    "trajectory": None,
                    "length": None,
                    "actions": []
                }
            ]
        }
        client.publish("robot/order", json.dumps(data))

    def test_order_2_2(self):
        client = mqtt.Client()
        client.connect("127.0.0.1", 1883, 60)
        data = {
            "headerId": 1,
            "timestamp": "1234567",
            "version": "2.0.0",
            "manufacturer": "seer",
            "serialNumber": "AMB-01",
            "orderId": "man-20230531123-3",
            "orderUpdateId": 4,
            "nodes": [
                {
                    "nodeId": "AP105",
                    "sequenceId": 4,
                    "released": True,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B4"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM97",
                    "sequenceId": 5,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM96",
                    "sequenceId": 6,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "AP104",
                    "sequenceId": 7,
                    "released": True,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B5"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                },
            ],
            "edges": [
                {
                    "edgeId": "e1",
                    "sequenceId": 0,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                },
                {
                    "edgeId": "e2",
                    "sequenceId": 2,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                }
            ]
        }
        client.publish("robot/order", json.dumps(data))

    def test_order_3_1(self):
        client = mqtt.Client()
        client.connect("127.0.0.1", 1883, 60)
        data = {
            "headerId": 1,
            "timestamp": "1234567",
            "version": "2.0.0",
            "manufacturer": "seer",
            "serialNumber": "AMB-01",
            "orderId": "man-20230531123-4",
            "orderUpdateId": 2,
            "nodes": [
                {
                    "nodeId": "LM99",
                    "sequenceId": 1,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM98",
                    "sequenceId": 2,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM97",
                    "sequenceId": 3,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "AP105",
                    "sequenceId": 4,
                    "released": True,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B4"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM97",
                    "sequenceId": 5,
                    "released": False,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM96",
                    "sequenceId": 6,
                    "released": False,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "AP104",
                    "sequenceId": 7,
                    "released": False,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B5"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                },
            ],
            "edges": [
                {
                    "edgeId": "e1",
                    "sequenceId": 0,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                },
                {
                    "edgeId": "e2",
                    "sequenceId": 2,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                }
            ]
        }
        client.publish("robot/order", json.dumps(data))

    def test_order_3_2(self):
        client = mqtt.Client()
        client.connect("127.0.0.1", 1883, 60)
        data = {
            "headerId": 1,
            "timestamp": "1234567",
            "version": "2.0.0",
            "manufacturer": "seer",
            "serialNumber": "AMB-01",
            "orderId": "man-20230531123-4",
            "orderUpdateId": 4,
            "nodes": [
                {
                    "nodeId": "AP105",
                    "sequenceId": 4,
                    "released": True,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B4"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM97",
                    "sequenceId": 5,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM96",
                    "sequenceId": 6,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "AP104",
                    "sequenceId": 7,
                    "released": True,
                    "actions": [
                        {
                            "actionType": "pick",
                            "actionId": str(uuid.uuid4()),
                            "blockingType": "HARD",
                            "actionParameters": [
                                {
                                    "key": "stationName",
                                    "value": "GPC-B-B5"
                                },
                                {
                                    "key": "stationType",
                                    "value": "ForkLoad"
                                }
                            ],
                            "actionDescription": "pick item"
                        }
                    ],
                    "nodeDescription": ""
                },
            ],
            "edges": [
                {
                    "edgeId": "e1",
                    "sequenceId": 0,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                },
                {
                    "edgeId": "e2",
                    "sequenceId": 2,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                }
            ]
        }
        client.publish("robot/order", json.dumps(data))

    def test_order_4_1(self):
        client = mqtt.Client()
        client.connect("127.0.0.1", 1883, 60)
        data = {
            "headerId": 1,
            "timestamp": "1234567",
            "version": "2.0.0",
            "manufacturer": "seer",
            "serialNumber": "AMB-01",
            "orderId": "man-20230531123-5",
            "orderUpdateId": 4,
            "nodes": [
                {
                    "nodeId": "LM96",
                    "sequenceId": 4,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM97",
                    "sequenceId": 5,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM98",
                    "sequenceId": 6,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "LM99",
                    "sequenceId": 7,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
                {
                    "nodeId": "AP107",
                    "sequenceId": 7,
                    "released": True,
                    "actions": [],
                    "nodeDescription": ""
                },
            ],
            "edges": [
                {
                    "edgeId": "e1",
                    "sequenceId": 0,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                },
                {
                    "edgeId": "e2",
                    "sequenceId": 2,
                    "edgeDescription": "",
                    "released": True,
                    "startNodeId": "",
                    "endNodeId": "",
                    "actions": []
                }
            ]
        }
        client.publish("robot/order", json.dumps(data))

    def test_order_5_1_0625(self):
        """
        读取文件，发送任务
        :return:
        """
        client = mqtt.Client()
        client.connect("192.168.8.152", 1883, 60)
        import json
        import os

        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")
        json_filename = 'test.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
        client.publish("robot/order", json.dumps(json_content))




if __name__ == '__main__':
    unittest.main()

import configparser
import copy
import datetime
import json
import uuid

from rbklib.rbklib import Rbklib
from type.VDA5050 import order, state

import networkx as nx

import os
import glob


def get_map_path1():
    current_directory = os.getcwd()
    pj_path = os.path.dirname(os.path.abspath(current_directory))
    return os.path.join(os.path.join(pj_path, "serve"),"robotMap")


def search_smap_files(folder):
    # 使用 glob 模块匹配符合条件的文件路径列表
    smap_files = glob.glob(os.path.join(folder, '*.smap'))

    if smap_files:
        print("找到以下 .smap 文件:")
        for file in smap_files:
            print(file)
            return file
    else:
        print("未找到 .smap 文件")




class SimOrder:

    def __init__(self, ip="192.168.4.64"):

        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.getcwd()), 'config.ini')
        # 读取配置文件
        config.read(config_path)
        ip = config.get('robot', 'robot_ip') if config.get('robot', 'robot_ip') else ip
        print(ip)
        self.rbk = Rbklib(ip)
        self.map = Map(self.get_map_path()) if self.rbk.so_19204 else Map(search_smap_files(get_map_path1()))
        self.loc = None
        self.init_point = ""
        self.node_point_id = dict()
        self.map_pos = map_pos(self.get_map_path())

    @staticmethod
    def get_map_path():
        current_directory = os.getcwd()
        pj_path = os.path.dirname(os.path.abspath(current_directory))
        return os.path.join(pj_path, "serve/robotMap/robot_map.smap")

    def creat_order3(self, tasks: list, released: bool = True, order_count: int = 1):
        # 获取机器人当前位置
        _, res = self.rbk.robot_status_loc_req()
        res_json = json.loads(res)
        current_station = res_json["current_station"]
        last_station = res_json["last_station"]
        if current_station:
            self.init_point = current_station
        else:
            self.init_point = last_station
        mid_pos = self.init_point
        # 遍历所有节点的任务
        sequenceId = 0
        orderId = str(uuid.uuid4())
        headerId = 0
        orderUpdateId = 0
        orders_1 = order.Order(headerId=headerId,
                               timestamp=datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z',
                               version="2.0.0",
                               manufacturer="",
                               serialNumber="",
                               orderId=orderId,
                               orderUpdateId=orderUpdateId,
                               nodes=[],
                               edges=[])
        p_all = []
        action_list = dict()
        print(tasks)
        for index, task in enumerate(tasks):
            action_list[task[0]] = task[1]
            if index == 0:
                paths = self.map.shortest_path(mid_pos, task[0])
            else:
                print("1----", p_all[-1], task[0])
                paths = self.map.shortest_path(p_all[-1], task[0])
                print("2----", paths)
            if index != 0 and index != len(tasks):
                paths = paths[1:]
            print(paths)
            p_all += paths
        print(p_all)
        # 预先生成nodeID
        for i, p in enumerate(p_all):
            self.node_point_id[p] = str(uuid.uuid4())

        for index, loc in enumerate(p_all):
            print(index, loc)
            print(self.node_point_id)
            params = action_list.get(loc)

            # 开始生成node、edge、action
            pos = self.map_pos.get(loc)
            # print(p, pos)
            # print(i)
            # 生成第一个node
            # index == 0 为了避免重复生成node
            if index == 0:
                node = order.Node(nodeId=self.node_point_id[loc],
                                  sequenceId=sequenceId,
                                  released=True,
                                  actions=[],
                                  nodePosition=state.NodePosition(**{
                                      "x": pos["x"],
                                      "y": pos["y"],
                                      "theta": -0.026340157,
                                      "allowedDeviationXY": 0.5,
                                      "allowedDeviationTheta": 0.5,
                                      "mapId": "01632ba1-5e0f-41b3-9d1c-b701fa168c3f",
                                      "mapDescription": "Id: 01632ba1-5e0f-41b3-9d1c-b701fa168c3f"
                                  }),
                                  nodeDescription=loc)
                orders_1.nodes.append(node)
            # 交替生成node和edge
            else:
                sequenceId += 1
                edge = order.Edge(edgeId=str(uuid.uuid4()),
                                  sequenceId=sequenceId,
                                  edgeDescription=p_all[index - 1] + "-" + p_all[index],
                                  released=False,
                                  startNodeId=self.node_point_id[p_all[index - 1]],
                                  endNodeId=self.node_point_id[p_all[index]])
                orders_1.edges.append(edge)

                sequenceId += 1
                node = order.Node(nodeId=self.node_point_id[loc],
                                  sequenceId=sequenceId,
                                  released=False,
                                  actions=[],
                                  nodePosition=state.NodePosition(**{
                                      "x": pos["x"],
                                      "y": pos["y"],
                                      "theta": -0.026340157,
                                      "allowedDeviationXY": 0.5,
                                      "allowedDeviationTheta": 0.5,
                                      "mapId": "01632ba1-5e0f-41b3-9d1c-b701fa168c3f",
                                      "mapDescription": "Id: 01632ba1-5e0f-41b3-9d1c-b701fa168c3f"
                                  }),
                                  nodeDescription=loc)
                # 注意，这里没有边的动作
                if params:
                    a = order.Action.creat()
                    a.actionId = str(uuid.uuid4())
                    a.actionType = "pick"
                    a.actionParameters = params
                    node.actions.append(a)
                orders_1.nodes.append(node)
        print("order:", json.dumps(orders_1.dict()))
        order_list = []
        # order 是一个完整的任务，节点全是base

        # 下面生成订单数量
        nodes_len = orders_1.nodes.__len__()
        edge_len = orders_1.edges.__len__()
        print(nodes_len, edge_len)
        if nodes_len - 1 != edge_len:
            print("生成的order异常：", nodes_len, edge_len, json.dumps(orders_1.dict()))
        if order_count > nodes_len - 1:
            order_count = nodes_len
        if 1 < order_count <= nodes_len - 1 and nodes_len > 3 and released:

            # 用python写程序，输入两个变量是：列表[]和int，列表元素是字典{"base":True}。
            # 需要做的是，输入[]，和int，计算[]的长度，根据int的值生成对应对应数量的[],但是[]的内容base是不同的
            # 当int=1,[]的前1个base所有值都为True，剩下的都为False
            # 当int=2，[]的前1个base所有值都为True，剩下的都为False
            # 以此类推
            for i in range(order_count):
                if i == 0:
                    print("000000000000000000000000000000000000000000", order_count)
                    order_list.append(orders_1)
                    continue

                headerId += 1
                orderUpdateId += 1
                new_order = order.Order(headerId=headerId,
                                        timestamp=datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z',
                                        version="2.0.0",
                                        manufacturer="",
                                        serialNumber="",
                                        orderId=orders_1.orderId,
                                        orderUpdateId=orderUpdateId,
                                        nodes=[],
                                        edges=[])
                e_s = copy.deepcopy(orders_1.edges)
                n_s = copy.deepcopy(orders_1.nodes)
                for n in range(i):

                    n_s[n].released = True
                    if n == i - 1:
                        n_s[n + 1].released = True
                for e in range(i):
                    e_s[e].released = True
                new_order.nodes = n_s
                new_order.edges = e_s
                order_list.append(new_order)
        else:
            for n in orders_1.nodes:
                n.released = True
            for e in orders_1.edges:
                e.released = True
            order_list.append(orders_1)

        return order_list

    def creat_order(self, tasks: list, released: bool = True, order_count: int = 1,init = None,action_type="test"):
        # 获取机器人当前位置
        if self.rbk.so_19204:
            _, res = self.rbk.robot_status_loc_req()
            res_json = json.loads(res)
            current_station = res_json["current_station"]
            last_station = res_json["last_station"]
            print("current_station",current_station)
            if current_station:
                self.init_point = current_station
            else:
                if last_station:
                    self.init_point = last_station
        else:
            print("init", init)
            if init:
                self.init_point = init
            else:
                self.init_point = "AP1"
        mid_pos = self.init_point
        # 遍历所有节点的任务
        sequenceId = 0
        orderId = str(uuid.uuid4())
        headerId = 0
        orderUpdateId = 0
        orders_1 = order.Order(headerId=headerId,
                               timestamp=datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z',
                               version="2.0.0",
                               manufacturer="",
                               serialNumber="",
                               orderId=orderId,
                               orderUpdateId=orderUpdateId,
                               nodes=[],
                               edges=[])
        p_all = []
        action_list = dict()
        # print(tasks)
        for index, task in enumerate(tasks):
            action_list[task[0]] = task[1]
            if index == 0:
                print("index",mid_pos, "p",task[0])
                paths = self.map.shortest_path(mid_pos, task[0])
            else:
                print("1----", p_all[-1], task[0])
                paths = self.map.shortest_path(p_all[-1], task[0])
                print("2----", paths)
            if index != 0 and index != len(tasks):
                paths = paths[1:]
            # print(paths)
            p_all += paths
        print(p_all)
        # 预先生成nodeID
        for i, p in enumerate(p_all):
            self.node_point_id[p] = str(uuid.uuid4())

        for index, loc in enumerate(p_all):
            print(index, loc)
            print(self.node_point_id)
            params = action_list.get(loc)

            # 开始生成node、edge、action
            pos = self.map_pos.get(loc)
            # print(p, pos)
            # print(i)
            # 生成第一个node
            # index == 0 为了避免重复生成node
            if index == 0:
                node = order.Node(nodeId=self.node_point_id[loc],
                                  sequenceId=sequenceId,
                                  released=True,
                                  actions=[],
                                  nodePosition={
                                      "x": pos["x"],
                                      "y": pos["y"],
                                      "theta": -0.026340157,
                                      "allowedDeviationXY": 0.5,
                                      "allowedDeviationTheta": 0.5,
                                      "mapId": "01632ba1-5e0f-41b3-9d1c-b701fa168c3f",
                                      "mapDescription": "Id: 01632ba1-5e0f-41b3-9d1c-b701fa168c3f"
                                  },
                                  nodeDescription=loc)
                orders_1.nodes.append(node)
            # 交替生成node和edge
            else:
                sequenceId += 1
                edge = order.Edge(edgeId=str(uuid.uuid4()),
                                  sequenceId=sequenceId,
                                  edgeDescription=p_all[index - 1] + "-" + p_all[index],
                                  released=False,
                                  startNodeId=self.node_point_id[p_all[index - 1]],
                                  length=0.,
                                  endNodeId=self.node_point_id[p_all[index]])
                orders_1.edges.append(edge)

                sequenceId += 1
                node = order.Node(nodeId=self.node_point_id[loc],
                                  sequenceId=sequenceId,
                                  released=False,
                                  actions=[],
                                  nodePosition={
                                      "x": pos["x"],
                                      "y": pos["y"],
                                      "theta": -0.026340157,
                                      "allowedDeviationXY": 0.5,
                                      "allowedDeviationTheta": 0.5,
                                      "mapId": "01632ba1-5e0f-41b3-9d1c-b701fa168c3f",
                                      "mapDescription": "Id: 01632ba1-5e0f-41b3-9d1c-b701fa168c3f"
                                  },
                                  nodeDescription=loc)
                # 注意，这里没有边的动作
                if params:
                    a = order.Action.creat()
                    a.actionId = str(uuid.uuid4())
                    a.actionType = action_type
                    a.actionParameters = params
                    node.actions.append(a)
                orders_1.nodes.append(node)
        print("order:", json.dumps(orders_1.model_dump()))

        return self.creat_order_base_on(orders_1, order_count=order_count, released=released)

    def creat_order_base_on(self, orders_1: order.Order, order_count: int = 1, released: bool = True):
        order_list = []
        orderUpdateId = 0
        # order 是一个完整的任务，节点全是base
        headerId = 0
        # 下面生成订单数量
        nodes_len = orders_1.nodes.__len__()
        edge_len = orders_1.edges.__len__()
        print(nodes_len, edge_len, order_count)
        if nodes_len - 1 != edge_len:
            print("生成的order异常：", nodes_len, edge_len, json.dumps(orders_1.dict()))
        if order_count >= nodes_len:
            order_count = nodes_len
        if 1 < order_count <= nodes_len and nodes_len > 3 and released:
            print("分解")
            # 用python写程序，输入两个变量是：列表[]和int，列表元素是字典{"base":True}。
            # 需要做的是，输入[]，和int，计算[]的长度，根据int的值生成对应对应数量的[],但是[]的内容base是不同的
            # 当int=1,[]的前1个base所有值都为True，剩下的都为False
            # 当int=2，[]的前1个base所有值都为True，剩下的都为False
            # 以此类推
            for i in range(order_count):
                if i == 0:
                    print("000000000000000000000000000000000000000000", order_count)
                    order_list.append(orders_1)
                    continue

                headerId += 1
                orderUpdateId += 1
                new_order = order.Order(headerId=headerId,
                                        timestamp=datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z',
                                        version="2.0.0",
                                        manufacturer="",
                                        serialNumber="",
                                        orderId=orders_1.orderId,
                                        orderUpdateId=orderUpdateId,
                                        nodes=[],
                                        edges=[])
                e_s = copy.deepcopy(orders_1.edges)
                n_s = copy.deepcopy(orders_1.nodes)
                for n in range(i):

                    n_s[n].released = True
                    if n == i - 1:
                        n_s[n + 1].released = True
                for e in range(i):
                    e_s[e].released = True
                new_order.nodes = n_s
                new_order.edges = e_s
                order_list.append(new_order)
        else:
            for n in orders_1.nodes:
                n.released = True
            for e in orders_1.edges:
                e.released = True
            order_list.append(orders_1)
        return order_list


class Map:
    def __init__(self, m: str):
        node_list, edge_list = self.output_node_edge(m)
        print(node_list)
        print(edge_list)
        self.G = nx.DiGraph()  # 创建一个有向图
        self.G.add_nodes_from(node_list)  # 添加节点
        self.G.add_edges_from(edge_list)  # 添加边

    @staticmethod
    def output_node_edge(map: str):
        print(map)
        with open(map, "r") as f:
            map_data = json.load(f)
        node_list = []
        print(map_data)
        for node in map_data['advancedPointList']:
            node_list.append(node['instanceName'])
        edge_list = []
        for edge in map_data['advancedCurveList']:
            start_node = edge['startPos']['instanceName']
            end_node = edge['endPos']['instanceName']
            edge_list.append((start_node, end_node))
        # print(node_list)
        return node_list, edge_list

    def shortest_path(self, s, e):
        print("0000000000",s, e)
        return nx.shortest_path(self.G, source=s, target=e)


def map_pos(maps: str):
    with open(maps, "r") as f:
        map_data = json.load(f)
    nodes = dict()
    for node in map_data['advancedPointList']:
        nodes[node['instanceName']] = node["pos"]
    return nodes

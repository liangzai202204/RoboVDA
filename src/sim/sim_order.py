import datetime
import json
import uuid
from src.config.config import Config
from src.serve.robot import RobotMap, Robot
from src.type.VDA5050 import order
from src.parse_protobuf.Map2D import Map2D
import networkx as nx
import matplotlib.pyplot as plt


class SimOrder:

    def __init__(self, config: Config, robot: Robot):

        self.config: Config = config
        self.robot: Robot = robot
        self.map: RobotMap = robot.map
        self.G = nx.DiGraph()  # 创建一个有向图
        if self.map.node_list and self.map.edge_list:
            self.G.add_nodes_from(self.map.node_list)  # 添加节点
            self.G.add_edges_from(self.map.edge_list)  # 添加边
        self.shortest_path = []
        self.sequenceId_node = 0
        self.sequenceId_edge = 0
        # 绘制有向图
        pos = nx.spring_layout(self.G)  # 定义节点位置布局
        nx.draw_networkx_nodes(self.G, pos, node_color='r', node_size=500)  # 绘制节点
        nx.draw_networkx_edges(self.G, pos, edge_color='b')  # 绘制边
        nx.draw_networkx_labels(self.G, pos)  # 绘制节点标签

        plt.axis('off')  # 关闭坐标轴显示
        plt.show()  # 显示图形

    def get_sequenceId(self):
        self.sequenceId_node += 2
        self.sequenceId_edge = self.sequenceId_node - 1
        return self.sequenceId_node

    def find_path(self, start, end, selfPosition=None):
        # if selfPosition == "SELF_POSITION":
        #     self.shortest_path.append(selfPosition)
        self.shortest_path.extend(nx.shortest_path(self.G, start, end))

    def create_node(self, point, task=None):
        point_xy = self.map.advanced_point_list.get(point)
        if not point_xy:
            return None
        a_s = []
        if task:
            a = order.Action.creat()
            a.actionId = str(uuid.uuid4())
            a.actionType = task
            a_s.append(a)
        return order.Node(nodeId=point,
                          sequenceId=self.get_sequenceId(),
                          released=True,
                          actions=a_s,
                          nodePosition={
                              "x": point_xy["x"],
                              "y": point_xy["y"],
                              "theta": point_xy["dir"],
                              "allowedDeviationXY": 0.5,
                              "allowedDeviationTheta": 0.5,
                              "mapId": self.map.current_map,
                              "mapDescription": f"md5: {self.map.current_map_md5}"
                          },
                          nodeDescription=point)

    def create_edge(self, startNodeId, endNodeId):
        e = order.Edge(edgeId=f"{startNodeId}-{endNodeId}",
                       sequenceId=self.sequenceId_edge,
                       edgeDescription=f"{startNodeId}-{endNodeId}",
                       released=True,
                       startNodeId=startNodeId,
                       length=0.,
                       endNodeId=endNodeId)
        print(e.model_dump())
        return e

    def creat_order(self, massage: dict):
        """
        :param massage:massage = {
            "id":"",
            "source_id":"",
            ...
        }
        """
        start = massage.get("source_id")
        end = massage.get("id")
        task = massage.get("task")
        try:
            if not self.robot.robot_push_msg.current_station and not start:
                start = "SELF_POSITION"
            if self.robot.robot_push_msg.current_station != start:
                start = self.robot.robot_push_msg.current_station
            if self.robot.robot_push_msg.current_station and not start:
                start = self.robot.robot_push_msg.current_station
            print(f"start:{start}")
            print(f"end:{end}")
            if not self.map.advanced_point_list.get(start) and not self.map.advanced_point_list.get(end):
                print("起点或者终点不在地图中")
                return
            self.find_path(start, end)
            nodes = []
            edges = []
            if self.shortest_path:
                print("线路", self.shortest_path)
                for i, p in enumerate(self.shortest_path):
                    if i + 1 == len(self.shortest_path):
                        nodes.append(self.create_node(p, task))
                    else:
                        nodes.append(self.create_node(p))
                    if len(nodes) >= 2:
                        edges.append(self.create_edge(self.shortest_path[i - 1], self.shortest_path[i]))
                orders_1 = order.Order(headerId=0,
                                       timestamp=datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z',
                                       version="2.0.0",
                                       manufacturer="",
                                       serialNumber="",
                                       orderId=str(uuid.uuid4()),
                                       orderUpdateId=1,
                                       nodes=nodes,
                                       edges=edges)
                print(orders_1.model_dump())
                self.shortest_path.clear()
                return orders_1
        except Exception as e:
            print(e)
        else:
            print("当前没有点")
        return None


class Map:
    def __init__(self, m: str):
        node_list, edge_list = self.output_node_edge(m)
        # print(node_list)
        # print(edge_list)
        self.G = nx.DiGraph()  # 创建一个有向图
        self.G.add_nodes_from(node_list)  # 添加节点
        self.G.add_edges_from(edge_list)  # 添加边
        print(m)
        with open(m, "r") as f:
            map_data = json.load(f)
        self.map = Map2D(map_data)
        self.advanced_point_list = {
            str(point.instance_name): {
                "x": point.pos.x,
                "y": point.pos.y,
                "z": point.pos.z,
                "dir": point.dir
            } for point in self.map.advanced_point_list
        }
        self.node_list = [instance.instance_name for instance in self.map.advanced_point_list]
        self.edge_list = [(acl.start_pos.instance_name, acl.end_pos.instance_name) for acl in
                          self.map.advanced_curve_list]

    @staticmethod
    def output_node_edge(map: str):
        # print(map)
        with open(map, "r") as f:
            map_data = json.load(f)
        node_list = []
        # print(map_data)
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
        print("0000000000", s, e)
        return nx.shortest_path(self.G, source=s, target=e)


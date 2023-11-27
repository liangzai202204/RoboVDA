import copy
import uuid
import threading
from typing import List
from src.config.config import Config
from src.pack.action_type import ActionPack, ActionType
from src.type.VDA5050 import order
from src.log.log import MyLogger
from src.serve.robot import Robot as Robot


class PackTask:
    def __init__(self, config: Config):
        self.config = config
        self.robot: Robot = None
        self.nodes_point = None
        self.order = None
        self.nodes: List[order.Node] = []
        self.edges: List[order.Edge] = []
        self.nodes_edges_list = []
        self.task_pack_list = []
        self.error = None
        self.log = MyLogger()
        self.lock = threading.Lock()
        self.uuid_task = {}

    def pack(self, new_order: order.Order, robot: Robot) -> (list, dict):
        with self.lock:
            try:
                if not self.robot:
                    self.robot = robot
                self.clear_pack()
                if not self.order:
                    self.order = new_order
                if self.order.orderId != new_order.orderId:
                    self.uuid_task = {}
                self.nodes = copy.deepcopy(new_order.nodes)
                self.edges = copy.deepcopy(new_order.edges)
                # 检查 order 内容 并排序 nodes 和 edges
                if not self.nodes and not self.edges:
                    return [], {}
                if (len(self.nodes) - 1) != len(self.edges):
                    return [], {}
                self.nodes.sort(key=lambda x: x.sequenceId)
                self.edges.sort(key=lambda y: y.sequenceId)
                self._pack()
                return self.task_pack_list, self.uuid_task
            except Exception as e:
                self.log.error(f"[pack]pack error ;{e}")
                return [], {}

    def _pack(self):
        try:
            self.task_pack_list.clear()
            """先从 edges 遍历，在edge中找到 startNode 和 endNode,
                    然后再打包
            """
            if self.nodes[0].actions:
                if self.nodes[0].released:
                    for a in self.nodes[0].actions:
                        action_uuid = str(uuid.uuid4())

                        a_task = ActionPack.pack_action(a, action_uuid, self.robot, self.config)
                        if a_task:
                            self.uuid_task[action_uuid] = a.actionId
                            self.task_pack_list.append(a_task)

            for edge in self.edges:
                if edge.released:
                    tag_edge_node_task = False
                    startNode = self._get_node(edge.startNodeId)
                    endNode = self._get_node(edge.endNodeId)
                    #  pick on endNode,need combine startNode and endNode,when actionType and agvClass was jack or fork
                    for endNode_a in endNode.actions:
                        if (endNode_a.actionType == ActionType.PICK or endNode_a.actionType == ActionType.DROP) and \
                                (self.robot.model.agvClass == "FORKLIFT" or self.robot.model.agvClass == "CARRIER"):
                            edge_uuid = str(uuid.uuid4())
                            edge_task = ActionPack.pack_edge(edge, startNode,
                                                             endNode, edge_uuid, self.robot, self.config
                                                             )
                            if edge_task:
                                self.uuid_task[edge_uuid] = edge.edgeId
                                self.task_pack_list.append(edge_task)
                            tag_edge_node_task = True
                            break
                    if tag_edge_node_task:
                        continue
                    edge_uuid = str(uuid.uuid4())
                    edge_task = ActionPack.pack_edge(edge, startNode.nodePosition,
                                                     endNode.nodePosition, edge_uuid, self.robot, self.config)
                    if edge_task:
                        self.uuid_task[edge_uuid] = edge.edgeId
                        self.task_pack_list.append(edge_task)
                    if endNode.actions and endNode.released:
                        for a2 in endNode.actions:
                            if a2.actionId not in self.uuid_task:
                                action_uuid = str(uuid.uuid4())
                                a_task = ActionPack.pack_action(a2, self.robot.model.agvClass, action_uuid)
                                if a_task:
                                    self.uuid_task[action_uuid] = a2.actionId
                                    self.task_pack_list.append(a_task)
        except Exception as e:
            self.log.error(f"pack_params error:{e}")

    def clear_pack(self):
        self.nodes = []
        self.edges = []
        self.nodes_edges_list = []
        self.task_pack_list = []

    def _get_node(self, NodeId):
        for node in self.nodes:
            if node.nodeId == NodeId:
                return node

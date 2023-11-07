import copy
import uuid
import threading
from typing import List, Union

from action_type.action_type import ActionPack
from type.moveTaskList import Task
from type.VDA5050 import order
from error_type import error_type as err
from log.log import MyLogger


class PackTask:
    def __init__(self):
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

    def pack(self, new_order: order.Order) -> (list, dict):
        with self.lock:
            try:
                self.clear_pack()
                if not self.order:
                    self.order = new_order
                if self.order.orderId != new_order.orderId:
                    self.uuid_task = {}
                self.nodes = copy.deepcopy(new_order.nodes)
                self.edges = copy.deepcopy(new_order.edges)
                # 检查 order 内容 并排序 nodes 和 edges
                if not self.nodes and not self.edges:
                    return [],{}
                if (len(self.nodes) - 1) != len(self.edges):
                    return [],{}
                self.nodes.sort(key=lambda x: x.sequenceId)
                self.edges.sort(key=lambda y: y.sequenceId)
                self._pack()
                return self.task_pack_list, self.uuid_task
            except Exception as e:
                self.log.error(f"[pack]pack error ;{e}")
                return [],{}

    def _pack(self):
        try:
            """先从 edges 遍历，在edge中找到 startNode 和 endNode,
                    然后再打包
            """

            if self.nodes.__len__() == 1:
                if self.nodes[0].actions:
                    if self.nodes[0].released:
                        for a in self.nodes[0].actions:
                            a_task = ActionPack.pack(a)
                            if a_task:
                                self.uuid_task[a.actionId] = str(uuid.uuid4())
                                self.task_pack_list.append(a_task)
                return

            for edge in self.edges:
                if edge.released:
                    startNode = self._get_node(edge.startNodeId)
                    endNode = self._get_node(edge.endNodeId)
                    if startNode.actions:
                        for a in startNode.actions:
                            a_task = ActionPack.pack(a)
                            if a_task:
                                if a.actionId not in self.uuid_task:
                                    self.uuid_task[a.actionId] = str(uuid.uuid4())
                                    self.task_pack_list.append(a_task)
                    edge_task = ActionPack.pack_edge(edge, startNode.nodePosition, endNode.nodePosition)
                    if edge_task:
                        self.uuid_task[edge.edgeId] = str(uuid.uuid4())
                        self.task_pack_list.append(edge_task)
                    if endNode.actions and endNode.released:
                        for a in endNode.actions:
                            a_task = ActionPack.pack(a)
                            if a_task:
                                self.uuid_task[a.actionId] = str(uuid.uuid4())
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

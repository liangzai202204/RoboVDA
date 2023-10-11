import threading
from typing import Union, List

import pydantic
from type.RobotOrderStatus import RobotOrderStatus
from type import order, state
from type.RobotOrderStatus import Status
from log.log import MyLogger


class OrderStateMachine:
    """ 状态机
    需要更新 node、edge、action 三个状态
    其中，action 有三部分来源，分别是 node、edge、instantAction

    """

    def __init__(self):
        self.status = None
        self.nodes: dict[str,order.Node] = {}
        self.edges: dict[str,order.Edge] = {}
        self.actions: dict[str, Union[order.Action, Status]] = {}
        self.log = MyLogger()

    def add_node(self, n_node: order.Node):
        """添加原生的 node，和 order 保持一致
        :param n_node:
        :return:
        """
        self.nodes[n_node.nodeId] = n_node

    def add_edge(self, n_edge: order.Edge):
        self.edges[n_edge.edgeId] = n_edge

    def add_action(self, n_action: order.Action):
        self.actions[n_action.actionId] = n_action
        self.actions["status"] = Status.INITIALIZING

    def add_order(self,n_order:order.Order):
        """将所有的node、edge、action添加到状态机
        :param n_order:
        :return:
        """
        # 添加所有的 node
        for n in n_order.nodes:
            self.add_node(n)
            if n.actions:
                for a in n.actions:
                    self.add_action(a)
        # 添加所有的 edge
        for e in n_order.edges:
            self.add_edge(e)
            if e.actions:
                for a in e.actions:
                    self.add_action(a)

    def del_node(self,ids:str):
        self.nodes.pop(ids)

    def del_edge(self,ids:str):
        self.edges.pop(ids)

    def del_action(self,ids:str):
        self.actions.pop(ids)

    def set_action_status(self,ids: str, status: Status):
        if self.actions.get(ids,None):
            self.actions[ids]["status"] = status
        else:
            self.log.error(f"当准备改变 action 状态是，找不到对应的actionId：{ids}")


class OrderStatus(pydantic.BaseModel):
    orderId: str
    status: Status
    nodes: dict[str, dict[str, Union[order.Node, Status]]]
    edges: dict[str, dict[str, Union[order.Edge, Status]]]
    actions: dict[str, dict[str, Union[order.Action, Status]]]
    lastNode: dict[str, Union[str, int, float]]

    def get_task_by_id(self, ids: str):
        # get edge or action
        if self.edges.get(ids, {}):
            return self.edges.get(ids, {}).get("edge")
        return self.actions.get(ids, {}).get("action")

    def get_node_by_id(self, ids: str):
        return self.nodes.get(ids, {}).get("node")

    def get_status_by_id(self, ids: str):
        return self.nodes.get(ids, {}).get("status")

    def get_edge_by_id(self, ids: str):
        return self.edges.get(ids, {}).get("edge")

    def get_edge_status_by_id(self, ids: str):
        return self.edges.get(ids, {}).get("status")

    def set_node_status_by_id(self, ids: str, status: Status):
        n = self.nodes.get(ids, {})
        n["status"] = status

    def set_edge_status_by_id(self, ids: str, status: Status):
        e = self.edges.get(ids, {})
        e["status"] = status
        ed = self.get_edge_by_id(ids)
        if ed.actions:
            for a in ed.actions:
                self.set_action_status_by_id(a.actionId, status)

    def set_action_status_by_id(self, ids: str, status: Status):
        e = self.actions.get(ids, {})
        e["status"] = status

    def set_node_and_edge_status(self, task: Union[order.Edge, order.Action], status: Status):
        if isinstance(task, order.Edge):
            self.set_node_status_by_id(task.startNodeId, status)
            self.set_last_node(task.startNodeId)
            self.set_node_status_by_id(task.endNodeId, status)
            self.set_edge_status_by_id(task.edgeId, status)
        elif isinstance(task, order.Action):
            self.set_action_status_by_id(task.actionId, status)
        else:
            print(f"error when set status,{type(task)}")

    def set_last_node(self, ids: str):
        try:
            n = self.nodes.get(ids, {})
            task = n["node"]
            if isinstance(task, order.Node):
                self.lastNode["nodeId"] = task.nodeId
                self.lastNode["sequenceId"] = task.sequenceId
        except Exception as e:
            self.lastNode["nodeId"] = ""
            self.lastNode["sequenceId"] = 0
            MyLogger().error(f"set_last_node error:{e}")

    def remove_node_by_id(self, ids: str):
        self.nodes.pop(ids)

    def remove_edge_by_id(self, ids: str):
        self.edges.pop(ids)

    def add_node(self, node: order.Node, task_id: list, task_id_all: list):
        self.nodes[node.nodeId] = {
            "node": node,
            "status": Status.INITIALIZING
        }
        task_id_all.append(node.nodeId)
        if node.actions:
            for a in node.actions:
                task_id.append(a.actionId)
                self.add_action(a)

    def add_edge(self, edge: order.Edge):
        self.edges[edge.edgeId] = {
            "edge": edge,
            "status": Status.INITIALIZING
        }
        if edge.actions:
            for a in edge.actions:
                self.add_action(a)

    def add_action(self, action: order.Action):
        self.actions[action.actionId] = {
            "action": action,
            "status": Status.INITIALIZING
        }

    def action_empty(self) -> bool:
        for ids, a in self.actions.items():
            a_s = a.get("status", None)
            if a_s != Status.FINISHED or a_s != Status.FAILED:
                return False
        return True


class Orders(pydantic.BaseModel):
    orders: OrderStatus

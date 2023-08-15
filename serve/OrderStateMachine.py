from enum import Enum
from typing import List, Union

import pydantic
from type.RobotOrderStatus import RobotOrderStatus
from type import order
from type import state


class Status(str, Enum):
    WAITING = "WAITING"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"


class OrderStateMachine:
    def __init__(self):
        self.orders = Orders
        self.task_id_list = []  # 包含所有 nodes，edges，actions 的所有 id
        self.edges_and_actions_id_list = []  # 只包含 edges，actions 的所有 id
        self.state = state.State

    def init_order(self, order_data: order.Order):
        order_id = order_data.orderId
        order_s = OrderStatus(**{
            "orderId": order_id,
            "status": Status.INITIALIZING,
            "nodes": {},
            "edges": {},
            "actions": {}
        })

        nodes = dict()
        edges = dict()
        actions = dict()
        for node in order_data.nodes:
            self.task_id_list.append(node.nodeId)
            nodes[node.nodeId] = {
                "node": node,
                "status": Status.FINISHED if node.sequenceId == 0 else Status.INITIALIZING
            }
            if node.actions:
                for action in node.actions:
                    self.task_id_list.append(action.actionId)
                    self.edges_and_actions_id_list.append(action.actionId)
                    actions[action.actionId] = {
                        "action":action,
                        "status":Status.INITIALIZING
                    }
        for edge in order_data.edges:
            self.task_id_list.append(edge.edgeId)
            self.edges_and_actions_id_list.append(edge.edgeId)
            edges[edge.edgeId] = {
                "node": edge,
                "status": Status.INITIALIZING
            }
            if edge.actions:
                for action in edge.actions:
                    self.task_id_list.append(action.actionId)
                    self.edges_and_actions_id_list.append(action.actionId)
                    actions[action.actionId] = {
                        "action":action,
                        "status":Status.INITIALIZING
                    }

        order_s.nodes = nodes
        order_s.edges = edges
        order_s.actions = actions
        self.orders.orders = order_s

    def update_state(self,robot_state:state.State) -> state.State:
        """
            傳入 robot_state，在robot_state 的基礎上，添加 nodesState，edgesState，actionsState
        :param robot_state: 這是包含事實是的機器人的信息的 state
        :return: state
        """
        nodes_status = self.orders.orders.nodes
        edges_status = self.orders.orders.edges
        actions_status = self.orders.orders.actions
        for _, node_s in nodes_status.items():
            n_s = node_s["status"]
            if n_s != Status.FINISHED:
                robot_state.nodeStates.append(state.NodeState(**node_s["node"].model_dump()))
        for _, edge_s in edges_status.items():
            e_s = edge_s["status"]
            if e_s != Status.FINISHED:
                robot_state.edgeStates.append(state.EdgeState(**edge_s["edge"].model_dump()))
        for _, action_s in actions_status.items():
            a_s = action_s["status"]
            a = action_s["action"]
            robot_state.actionStates.append(state.ActionState(**{
                "actionDescription": a.actionDescription,
                "actionId": a.actionId,
                "actionStatus":  a_s,
                "actionType": a.actionType,
                "resultDescription": ""
            }))
        return robot_state


    def update_order(self, order_data: order.Order):
        # 收到新的訂單，需要更新，在更新前，刪除所有不是released的node和edge
        self._del_not_released_items()

        # 添加新的node和edge
        new_edges = order_data.edges
        new_nodes = order_data.nodes

        for node in new_nodes:
            old_node = self.orders.orders.get_node_by_id(node.nodeId)
            if old_node:
                continue
            else:
                self.orders.orders.add_node(node)
                self.task_id_list.append(node.nodeId)
        for edge in new_edges:
            old_edge = self.orders.orders.get_node_by_id(edge.nodeId)
            if old_edge:
                continue
            else:
                self.orders.orders.add_edge(edge)
                self.task_id_list.append(edge.edgeId)
                self.edges_and_actions_id_list.append(edge.edgeId)

    def update_order_status(self,task_pack_status:dict):
        if not (isinstance(task_pack_status, list) and len(task_pack_status) != 0):
            print("更新出錯update_order_status ，任務内容不對",task_pack_status)
            return
        for task_statu in task_pack_status:
            task_id = task_statu["task_id"]
            c_edge = self.orders.orders.get_edge_by_id(task_id)  # 獲得order中的，edge，然後找出 起點的 nodeId 和終點的 nodeId
            if not c_edge:
                print("嘗試更新edge，但是沒有這個edge，id：",task_id)
                raise
            if task_statu["status"] == RobotOrderStatus.Completed:
                self.orders.orders.set_node_and_edge_status(c_edge,Status.FINISHED)
            elif task_statu["status"] == RobotOrderStatus.Failed:
                self.orders.orders.set_node_and_edge_status(c_edge, Status.FAILED)
            elif task_statu["status"] == RobotOrderStatus.StatusNone:
                self.orders.orders.set_node_and_edge_status(c_edge, Status.INITIALIZING)
            elif task_statu["status"] == RobotOrderStatus.Running:
                self.orders.orders.set_node_and_edge_status(c_edge, Status.RUNNING)
            elif task_statu["status"] == RobotOrderStatus.Canceled:
                self.orders.orders.set_node_and_edge_status(c_edge, Status.FAILED)
            elif task_statu["status"] == RobotOrderStatus.Suspended:
                self.orders.orders.set_node_and_edge_status(c_edge, Status.PAUSED)
            elif task_statu["status"] == RobotOrderStatus.NotFound:
                self.orders.orders.set_node_and_edge_status(c_edge, Status.FAILED)
            else:
                print("未知狀態：",task_statu["status"])
                raise


    def _del_not_released_items(self):
        edges = self.orders.orders.edges
        nodes = self.orders.orders.nodes
        for ids, node_s in nodes.items():
            node2 = node_s["node"]
            if isinstance(node2, order.Node):
                if not node2.released:
                    self.task_id_list.remove(ids)
                    nodes.pop(ids)
        for ids, edge_s in edges.items():
            edge2 = edge_s["edge"]
            if isinstance(edge2, order.Node):
                if not edge2.released:
                    self.task_id_list.remove(ids)
                    self.edges_and_actions_id_list.remove(ids)
                    edges.pop(ids)


class OrderStatus(pydantic.BaseModel):
    orderId: str
    status: Status
    nodes: dict[str, dict[str, Union[order.Node, Status]]]
    edges: dict[str, dict[str, Union[order.Edge, Status]]]
    actions: dict[str, dict[str, Union[order.Action, Status]]]

    def get_node_by_id(self,ids:str):
        return self.nodes.get(ids, {}).get("node")

    def get_status_by_id(self,ids:str):
        return self.nodes.get(ids, {}).get("status")

    def get_edge_by_id(self,ids:str):
        return self.edges.get(ids, {}).get("edge")

    def get_edge_status_by_id(self,ids:str):
        return self.edges.get(ids, {}).get("status")

    def set_node_status_by_id(self,ids:str,status:Status):
        n = self.nodes.get(ids, {})
        n["status"] = status

    def set_edge_status_by_id(self,ids:str,status:Status):
        e = self.edges.get(ids, {})
        e["status"] = status

    def set_node_and_edge_status(self,edge:order.Edge,status:Status):
        self.set_node_status_by_id(edge.startNodeId,status)
        self.set_node_status_by_id(edge.endNodeId,status)
        self.set_node_status_by_id(edge.edgeId,status)


    def remove_node_by_id(self,ids:str):
        self.nodes.pop(ids)

    def remove_edge_by_id(self,ids:str):
        self.edges.pop(ids)

    def add_node(self,node:order.Node):
        self.nodes[node.nodeId] = {
            "node":node,
            "status":Status.INITIALIZING
        }

    def add_edge(self,edge:order.Edge):
        self.edges[edge.nodeId] = {
            "node":edge,
            "status":Status.INITIALIZING
        }






class Orders(pydantic.BaseModel):
    orders: OrderStatus
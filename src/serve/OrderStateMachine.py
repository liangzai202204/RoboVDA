import threading
from typing import Union, List

import pydantic
from src.type.RobotOrderStatus import RobotOrderStatus
from src.type import order,state
from src.type.RobotOrderStatus import Status
from src.log.log import MyLogger


class OrderStateMachine:
    def __init__(self):
        self.orders = Orders
        self.current_order = None
        self.task_id_list = []  # 包含所有 nodes，edges，actions 的所有 id
        self.edges_and_actions_id_list = []  # 只包含 edges，actions 的所有 id
        self.ready = True
        self.init = False
        self.lock = threading.Lock()
        self.log = MyLogger()
        self.cancel_order = None
        self.instant_action_stop_pause = None
        self.instant_action_start_pause = None

    def init_order(self, order_data: order.Order):
        with self.lock:
            # 清楚上次 cancelOrder 残留的信息
            if self.cancel_order:
                self.cancel_order = None
            self.current_order = order_data
            self.ready = False
            order_id = order_data.orderId
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
                            "action": action,
                            "status": Status.INITIALIZING
                        }
            for edge in order_data.edges:
                self.task_id_list.append(edge.edgeId)
                self.edges_and_actions_id_list.append(edge.edgeId)
                edges[edge.edgeId] = {
                    "edge": edge,
                    "status": Status.INITIALIZING
                }
                if edge.actions:
                    for action in edge.actions:
                        self.task_id_list.append(action.actionId)
                        self.edges_and_actions_id_list.append(action.actionId)
                        actions[action.actionId] = {
                            "action": action,
                            "status": Status.INITIALIZING
                        }
            try:
                self.orders.orders = OrderStatus(**{
                    "orderId": order_id,
                    "status": Status.INITIALIZING,
                    "nodes": nodes,
                    "edges": edges,
                    "actions": actions,
                    "lastNode":{}
                })
            except Exception as e:
                print("An error occurred:", str(e))

            self.init = True
            self.log.warning(f"OrderStateMachine init ok!!!")

    def update_state(self, robot_state: state.State) -> state.State:
        """
            傳入 robot_state，在robot_state 的基礎上，添加 nodesState，edgesState，actionsState
        :param robot_state: 這是包含事實是的機器人的信息的 state
        :return: state
        """

        if not isinstance(robot_state,state.State):
            self.log.error("robot_state:False")
            return robot_state
        if not self.init:
            print("not self.init")
            return robot_state
        with self.lock:

            # 每次更新state。都將state的内容清空，然後遍歷添加 state

            robot_state.nodeStates.clear()
            robot_state.edgeStates.clear()
            robot_state.actionStates.clear()



            if self.cancel_order:
                robot_state.actionStates.append(self.cancel_order)
            if self.instant_action_start_pause:
                robot_state.actionStates.append(self.instant_action_start_pause)
                if self.instant_action_stop_pause:
                    self.instant_action_start_pause = None
            if self.instant_action_stop_pause:
                robot_state.actionStates.append(self.instant_action_start_pause)
                if self.instant_action_start_pause:
                    self.instant_action_stop_pause = None
            if self.current_order:
                # 在 topic state 中更在 lastNode 字段
                robot_state.lastNodeId = self.orders.orders.lastNode.get("nodeId", "")
                robot_state.lastNodeSequenceId = self.orders.orders.lastNode.get("sequenceId", 0)
                # 統計每個node、edge、action 的完成數量
                nodes_status = self.orders.orders.nodes
                actions_status = self.orders.orders.actions
                edges_status = self.orders.orders.edges
                node_f_n = len(nodes_status)
                edge_f_n = len(edges_status)
                action_f_n = len(actions_status)
                if node_f_n == 0 and edge_f_n == 0 and self.orders.orders.action_empty():
                    self.log.error("狀態機沒有任務")
                    return robot_state
                for _, node_s in nodes_status.items():
                    n_s = node_s.get("status",None)
                    if n_s != Status.FINISHED:
                        robot_state.nodeStates.append(state.NodeState(**node_s["node"].model_dump()))
                    else:
                        node_f_n -= 1


                for _, edge_s in edges_status.items():
                    e_s = edge_s.get("status",None)
                    if e_s != Status.FINISHED:
                        robot_state.edgeStates.append(state.EdgeState(**edge_s["edge"].model_dump()))
                    else:
                        edge_f_n -= 1
                for _, action_s in actions_status.items():
                    a_s = action_s.get("status",None)
                    a = action_s.get("action",None)
                    robot_state.actionStates.append(state.ActionState(**{
                        "actionDescription": a.actionDescription,
                        "actionId": a.actionId,
                        "actionStatus": a_s,
                        "actionType": a.actionType,
                        "resultDescription": ""
                    }))
                    if a_s == Status.FINISHED or a_s == Status.FAILED:
                        action_f_n -= 1
                if len(nodes_status) == 1:
                    node_f_n = 0
                if node_f_n == 0 and edge_f_n == 0 and action_f_n == 0:

                    self.orders.orders.status = Status.FINISHED
                    self.ready = True
                    self.edges_and_actions_id_list.clear()
                    self.task_id_list.clear()
                    self.log.info(f"狀態機任務: {self.orders.orders.status}")
                    self.orders = Orders
                    self.init = True
                else:
                    self.orders.orders.status = Status.RUNNING
                    self.log.info(f"狀態機任務: {self.orders.orders.status}")
            if len(robot_state.nodeStates) == 0:
                robot_state.newBaseRequest = True
            else:
                print(robot_state.nodeStates)
                robot_state.newBaseRequest = False

            return robot_state

    def update_order(self, order_data: order.Order):
        if not self.init:
            return
            # 收到新的訂單，需要更新，在更新前，刪除所有不是released的node和edge
        if not isinstance(order_data,order.Order):
            self.log.error("not isinstance order_data :order.Order")
            return

        with self.lock:
            try:
                # 清楚上次 cancelOrder 残留的信息
                if self.cancel_order:
                    self.cancel_order = None
                if self.instant_action_start_pause:
                    self.instant_action_start_pause = None
                if self.instant_action_stop_pause:
                    self.instant_action_stop_pause = None

                self._del_not_released_items()
                # 添加新的node和edge
                new_edges = order_data.edges
                new_nodes = order_data.nodes
                for node in new_nodes:
                    if not self.orders.orders.get_node_by_id(node.nodeId):
                        self.orders.orders.add_node(node,self.task_id_list,self.edges_and_actions_id_list)
                for edge in new_edges:
                    if not self.orders.orders.get_edge_by_id(edge.edgeId):
                        self.orders.orders.add_edge(edge)
                        self.task_id_list.append(edge.edgeId)
                        self.edges_and_actions_id_list.append(edge.edgeId)
            except Exception as e:
                print(f"update_order:{e}")

    def update_order_status(self, task_pack_status: dict):
        if not self.init:
            return
        if not (isinstance(task_pack_status, list) and len(task_pack_status) != 0):
            self.log.error(f"更新出錯update_order_status ，任務内容不對{ task_pack_status}")
            return
        with self.lock:
            for task_statu in task_pack_status:
                task_id = task_statu.get("task_id")
                if self.current_order:
                    c_edge = self.orders.orders.get_task_by_id(task_id)  # 獲得order中的，edge，然後找出 起點的 nodeId 和終點的 nodeId
                    if not c_edge:
                        self.log.error(f"嘗試更新edge，但是沒有這個edgeId：{task_id}")
                        continue
                    if task_statu["status"] == RobotOrderStatus.Completed:
                        self.orders.orders.set_node_and_edge_status(c_edge, Status.FINISHED)
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
                    elif task_statu["status"] == RobotOrderStatus.Waiting:
                        self.orders.orders.set_node_and_edge_status(c_edge, Status.WAITING)
                    else:
                        s = task_statu["status"]
                        self.log.error(f"未知狀態：{s}")
                    if len(self.orders.orders.nodes) == 1 and self.orders.orders.action_empty():
                        self.orders.orders.set_node_status(Status.FINISHED)

    def set_cancel_order_instant_action(self,cancel_order_action:order.Action,status:Status):
        """对应 topic instantAction：cancelOrder
        应为 cancelOrder 含有actionID，并且 action 的状态要加入到 topic：state 中，和状态机的逻辑不符（订单状态机需要任务id更新state）
        所以，会在状态机单独存 cancelOrder的详细信息，在 update_order_status 时判断是否有 cancelOrder，如有则加入到 state中，
        同时，在调用此函数时，已经下发取消任务给机器人，所以 cancelOrder 的状态是 FINISHED，并且一直保持不变。在新订单来临时，
        清除 cancelOrder
        的内容。
        另外，还要将状态机的 nodeState 和 edgeState delete，将 actionState 的状态都改为 failed
        """
        with self.lock:
            self.init = True
            if self.init:
                a = cancel_order_action
                self.cancel_order = state.ActionState(**{
                        "actionDescription": a.actionDescription,
                        "actionId": a.actionId,
                        "actionStatus": status,
                        "actionType": a.actionType,
                        "resultDescription": ""
                    })
                if self.current_order:
                    # nodeState 和 edgeState delete
                    self.orders.orders.nodes = {}
                    self.orders.orders.edges = {}
                    self.task_id_list.clear()

                    self.orders.orders.status = Status.FINISHED
                    self.edges_and_actions_id_list.clear()
                    a_s = self.orders.orders.actions
                    for ids,action_s in a_s.items():
                        if action_s.get("status",None) and action_s["status"] != Status.FINISHED:
                            action_s["status"] = Status.FAILED



    def _del_not_released_items(self):
        if not self.init:
            return
        # 上鎖
        edges = self.orders.orders.edges
        nodes = self.orders.orders.nodes
        try:
            node_s_to_remove = []
            for ids, node_s in nodes.items():
                node2 = node_s.get("node")
                if not node2:
                    continue
                if isinstance(node2, order.Node):
                    if not node2.released:
                        self.task_id_list.remove(ids)
                        node_s_to_remove.append(ids)
            for key in node_s_to_remove:
                del nodes[key]
            edge_s_to_remove = []
            for ids, edge_s in edges.items():
                edge2 = edge_s.get("edge")
                if not edge2:
                    continue
                if isinstance(edge2, order.Node):
                    if not edge2.released:
                        self.task_id_list.remove(ids)
                        self.edges_and_actions_id_list.remove(ids)
                        edge_s_to_remove.append(ids)
        except Exception as e:
            self.log.error(f"_del_not_released_items:{e}")

    def clear(self):
        self.orders.orders = OrderStatus(**{
            "orderId": "",
            "status": Status.INITIALIZING,
            "nodes": {},
            "edges": {},
            "actions": {},
            "lastNode":{}
        })
        self.task_id_list = []
        self.edges_and_actions_id_list = []
        self.ready = True
        self.init = False

    def set_start_pause_instant_action(self, start_pause:order.Action,status:Status):
        with self.lock:
            if self.init:
                a = start_pause
                self.instant_action_start_pause = state.ActionState(**{
                        "actionDescription": a.actionDescription,
                        "actionId": a.actionId,
                        "actionStatus": status,
                        "actionType": a.actionType,
                        "resultDescription": ""
                    })
                if self.instant_action_stop_pause:
                    self.instant_action_stop_pause = None

    def set_stop_pause_instant_action(self,stop_pause:order.Action,status:Status):
        with self.lock:
            if self.init:
                a = stop_pause
                self.instant_action_stop_pause = state.ActionState(**{
                        "actionDescription": a.actionDescription,
                        "actionId": a.actionId,
                        "actionStatus": status,
                        "actionType": a.actionType,
                        "resultDescription": ""
                    })
                if self.instant_action_start_pause:
                    self.instant_action_start_pause = None


class OrderStatus(pydantic.BaseModel):
    orderId: str
    status: Status
    nodes: dict[str, dict[str, Union[order.Node, Status]]]
    edges: dict[str, dict[str, Union[order.Edge, Status]]]
    actions: dict[str, dict[str, Union[order.Action, Status]]]
    lastNode:dict[str,Union[str, int,float]]

    def get_task_by_id(self,ids: str):
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

    def set_node_status(self,status: Status):
        for node_id,node_key in self.nodes.items():
            self.set_node_status_by_id(node_id,status)


    def set_edge_status_by_id(self, ids: str, status: Status):
        e = self.edges.get(ids, {})
        e["status"] = status
        ed = self.get_edge_by_id(ids)
        if ed.actions:
            for a in ed.actions:
                self.set_action_status_by_id(a.actionId,status)

    def set_action_status_by_id(self, ids: str, status: Status):
        e = self.actions.get(ids, {})
        e["status"] = status

    def set_node_and_edge_status(self, task: Union[order.Edge,order.Action], status: Status):
        if isinstance(task,order.Edge):
            self.set_node_status_by_id(task.startNodeId, status)
            self.set_last_node(task.startNodeId)
            self.set_node_status_by_id(task.endNodeId, status)
            self.set_edge_status_by_id(task.edgeId, status)
        elif isinstance(task,order.Action):
            self.set_action_status_by_id(task.actionId,status)
        else:
            print(f"error when set status,{type(task)}")

    def set_last_node(self, ids:str):
        try:
            n = self.nodes.get(ids, {})
            task = n["node"]
            if isinstance(task,order.Node):
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

    def add_node(self, node: order.Node,task_id:list,task_id_all:list):
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
        for ids,a in self.actions.items():
            a_s = a.get("status",None)
            if a_s != Status.FINISHED or a_s != Status.FAILED:
                return False
        return True


class Orders(pydantic.BaseModel):
    orders: OrderStatus

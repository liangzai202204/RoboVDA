import threading
from typing import Union, List

import pydantic
from type.RobotOrderStatus import RobotOrderStatus
from type import order, state,pushMsgType
from type.RobotOrderStatus import Status
from log.log import MyLogger
from action_type.action_type import instant_action_type

class OrderStateMachine:
    """ 状态机
    需要更新 node、edge、action 三个状态
    其中，action 有三部分来源，分别是 node、edge、instantAction

    """

    def __init__(self):
        self.lock = threading.Lock()
        self.order = None
        self.status = None
        self.nodes: dict[str,order.Node] = {}
        self.edges: dict[str,order.Edge] = {}
        self.actions: dict[str, Union[state.ActionState, Status]] = {}
        self.instant_actions: dict[str, Union[state.ActionState, Status]] = {}
        self.log = MyLogger()
        self.nodes_ids = []
        self.edges_ids = []
        self.actions_ids = []
        self.last_node = None

    def add_node(self, n_node: order.Node):
        """添加原生的 node，和 order 保持一致
        :param n_node:
        :return:
        """
        if self.nodes.get(n_node.nodeId,None):
            self.log.warning(f"添加 node，但已存在")
            return
        self.nodes[n_node.nodeId] = n_node
        self.nodes_ids.append(n_node.nodeId)

    def add_edge(self, n_edge: order.Edge):
        if self.edges.get(n_edge.edgeId,None):
            self.log.warning(f"添加 edge，但已存在")
            return
        self.edges[n_edge.edgeId] = n_edge
        self.edges_ids.append(n_edge.edgeId)

    def add_action(self, n_action: order.Action):
        if self.actions.get(n_action.actionId,None):
            self.log.warning(f"添加 action，但已存在")
            return
        self.actions[n_action.actionId] = state.ActionState(**n_action.model_dump())
        self.actions_ids.append(n_action.actionId)

    def add_instant_action(self, n_action: order.Action):
        with self.lock:
            if self.instant_actions.get(n_action.actionId,None):
                self.log.warning(f"添加 action，但已存在,id:{n_action.actionId}")
                return
            self.instant_actions[n_action.actionId] = state.ActionState(**n_action.model_dump())

    def add_order(self,n_order:order.Order):
        """将所有的node、edge、action添加到状态机
        :param n_order:
        :return:
        """
        with self.lock:
            if not self.order:
                self.order = n_order
            if self.order.orderUpdateId <= n_order.orderUpdateId:
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
        if ids not in self.nodes_ids:
            self.log.warning(f"del_node :{ids}")
            return
        self.nodes.pop(ids)
        self.nodes_ids.remove(ids)

    def del_edge(self,ids:str):
        if ids not in self.edges_ids:
            self.log.warning(f"del_edge :{ids}")
            return
        self.edges.pop(ids)
        self.edges_ids.remove(ids)

    def del_action(self,ids:str):
        if ids not in self.actions_ids:
            self.log.warning(f"del_action :{ids}")
            return
        self.actions.pop(ids)
        self.actions_ids.remove(ids)

    def set_action_status(self,ids: str, status: Status):
        if self.actions.get(ids,None):
            self.actions[ids].actionStatus = status
        else:
            self.log.error(f"当准备改变 action 状态时，找不到对应的 actionId：{ids}")

    def set_instant_action_status(self,ids: str, status: Status):
        if self.instant_actions.get(ids,None):
            self.instant_actions[ids].actionStatus = status
        else:
            self.log.error(f"当准备改变 instant action 状态时，找不到对应的 actionId：{ids}")

    @property
    def actions_empty(self):
        if not self.actions:
            return True
        for ids,action in self.actions.items():
            if action.actionStatus != state.ActionStatus.FINISHED:
                return False
        return True

    def update_order_status(self, task_pack_status: pushMsgType.TaskStatusPackage):
        with self.lock:
            # 判断是否需要更新
            if not self.edges and self.actions_empty:
                self.log.info(f"[OrderStateMachine] order empty")
                self.nodes.clear()
                return
            task_status_list_id = []
            for task_status in task_pack_status.task_status_list:
                task_status_list_id.append(task_status.task_id)
            # 更新 edge 和 node
            if self.edges:
                need_del_edge_id = []
                need_update_edge_id = []
                # 当状态机的任务id，在 task_pack_status 中
                for e_id in self.edges_ids:
                    if e_id not in task_status_list_id:
                        if self.edges.get(e_id):
                            if self.edges[e_id].released:
                                need_del_edge_id.append(e_id)
                    else:
                        need_update_edge_id.append(e_id)
                print("need_del_edge_id",need_del_edge_id)
                print("need_update_edge_id",need_update_edge_id)
                for task_statu in task_pack_status.task_status_list:
                    if task_statu.task_id in need_update_edge_id:
                        if task_statu.status == RobotOrderStatus.Completed:

                            if self.edges.get(task_statu.task_id,None):
                                e = self.edges.get(task_statu.task_id)
                                self.last_node = self.nodes.get(e.endNodeId)
                                self.del_edge(task_statu.task_id)
                                self.del_node(e.startNodeId)
                                self.del_node(e.endNodeId)
                for del_edge_id in need_del_edge_id:
                    self.del_edge(del_edge_id)
            # 更新 action
            if not self.actions_empty:
                # 更新机器人当前的任务，这个任务是 action 任务（原地任务）
                for task_statu in task_pack_status.task_status_list:
                    if task_statu.task_id in self.actions_ids:
                        if task_statu.status == RobotOrderStatus.Completed:
                            self.set_action_status(task_statu.task_id,Status.FINISHED)
                        elif task_statu.status == RobotOrderStatus.Failed:
                            self.set_action_status(task_statu.task_id,Status.FAILED)
                        elif task_statu.status == RobotOrderStatus.StatusNone:
                            self.set_action_status(task_statu.task_id,Status.INITIALIZING)
                        elif task_statu.status == RobotOrderStatus.Running:
                            self.set_action_status(task_statu.task_id,Status.RUNNING)
                        elif task_statu.status == RobotOrderStatus.Canceled:
                            self.set_action_status(task_statu.task_id,Status.FAILED)
                        elif task_statu.status == RobotOrderStatus.Suspended:
                            self.set_action_status(task_statu.task_id,Status.PAUSED)
                        elif task_statu.status == RobotOrderStatus.NotFound:
                            self.set_action_status(task_statu.task_id,Status.FAILED)
                        elif task_statu.status == RobotOrderStatus.Waiting:
                            self.set_action_status(task_statu.task_id,Status.WAITING)
                        else:
                            self.log.warning(f"更新状态机 action 的状态时，找不到状态：{task_statu.status}")
            # 更新 instant action
            if self.instant_actions:
                for instant_action_id,instant_action in self.instant_actions.items():
                    if instant_action.actionType == 'cancelOrder':
                        instant_action.actionStatus = Status.FINISHED
                    elif instant_action.actionType == 'startPause':
                        instant_action.actionStatus = Status.FINISHED
                    elif instant_action.actionType == 'stopPause':
                        instant_action.actionStatus = Status.FINISHED
                    elif instant_action.actionType == 'initPosition':
                        for task_statu in task_pack_status.task_status_list:
                            if task_statu.task_id == instant_action_id:
                                self.update_instant_actions_status(instant_action_id,task_statu.status)

    def update_instant_actions_status(self,ids,status):
        if status == RobotOrderStatus.Completed:
            self.set_instant_action_status(ids, Status.FINISHED)
        elif status == RobotOrderStatus.Failed:
            self.set_instant_action_status(ids, Status.FAILED)
        elif status == RobotOrderStatus.StatusNone:
            self.set_instant_action_status(ids, Status.INITIALIZING)
        elif status == RobotOrderStatus.Running:
            self.set_instant_action_status(ids, Status.RUNNING)
        elif status == RobotOrderStatus.Canceled:
            self.set_instant_action_status(ids, Status.FAILED)
        elif status == RobotOrderStatus.Suspended:
            self.set_instant_action_status(ids, Status.PAUSED)
        elif status == RobotOrderStatus.NotFound:
            self.set_instant_action_status(ids, Status.FAILED)
        elif status == RobotOrderStatus.Waiting:
            self.set_instant_action_status(ids, Status.WAITING)
        else:
            self.log.warning(f"更新状态机 instant action 的状态时，找不到状态：{ids.status}")



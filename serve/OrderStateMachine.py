import threading
from typing import Union

from type.RobotOrderStatus import RobotOrderStatus
from type import pushMsgType
from type.VDA5050 import order, state
from type.RobotOrderStatus import Status
from action_type import action_type
from log.log import MyLogger


class OrderStateMachine:
    """ 状态机
    需要更新 node、edge、action 三个状态
    其中，action 有三部分来源，分别是 node、edge、instantAction

    """

    def __init__(self):
        self.uuid_task = {}
        self.taskStatus = None
        self.task_pack_status = None
        self.lock = threading.Lock()
        self.order = None
        self.status = None
        self.nodes: dict[str, order.Node] = {}
        self.edges: dict[str, order.Edge] = {}
        self.actions: dict[str, Union[state.ActionState, Status]] = {}
        self.instant_actions: dict[str, Union[state.ActionState, Status]] = {}
        self.log = MyLogger()
        self.last_node = None
        self.tasks_uuid = []

    def creat_order_uuid(self):
        """根据 order 生成任务 id
        order 中的 orderId 是任务的唯一id
        order 中的 相邻的 node-edge-node 组合成一个 3066任务，并且生成响应的 任务id--uuid
        根据 order 生成 n 个任务，就有 n 个 uuid。通过 uuid 就行任务状态管理

        :return: None
        """
        return

    def order_empty(self) -> bool:
        """是否有订单"""
        if not self.edges and not self.actions or not self.nodes:
            return True
        return False

    def order_task_empty(self) -> bool:
        """有订单，但是任务已完成"""
        if not self.edges and not self.actions or not self.nodes:
            return True
        if self.actions_empty and self.edges_empty and self.nodes_empty:
            return True
        return False

    def add_node(self, n_node: order.Node):
        """添加原生的 node，和 order 保持一致
        :param n_node:
        :return:
        """
        if self.nodes.get(n_node.nodeId, None):
            n = self.nodes.get(n_node.nodeId, None)
            if not n.released and not n_node.released:
                # self.log.warning(f"添加 node，但已存在")
                return
        self.nodes[n_node.nodeId] = n_node

    def add_edge(self, n_edge: order.Edge):
        if self.edges.get(n_edge.edgeId, None):
            e = self.edges.get(n_edge.edgeId, None)
            if not e.released and not n_edge.released:
                # self.log.warning(f"添加 edge，但已存在")
                return
        self.edges[n_edge.edgeId] = n_edge
        #  released 的 edge 單獨保存

    def add_action(self, n_action: order.Action):
        if self.actions.get(n_action.actionId, None):
            # self.log.warning(f"添加 action，但已存在")
            return
        if n_action.model_dump():
            self.actions[n_action.actionId] = state.ActionState(**n_action.model_dump())
        else:
            self.log.warning(f"添加 action，但是为空：{n_action.model_dump()}")

    def add_instant_action(self, n_action: order.Action, status=None):
        with self.lock:
            if status:
                a = state.ActionState(**n_action.model_dump())
                a.actionStatus = state.ActionStatus.FAILED
                self.instant_actions[n_action.actionId] = a
                return
            if self.instant_actions.get(n_action.actionId, None):
                self.log.warning(f"添加 action，但已存在,id:{n_action.actionId}")
                return
            self.instant_actions[n_action.actionId] = state.ActionState(**n_action.model_dump())

    def add_order(self, n_order: order.Order,uuid_task:dict):
        """将所有的node、edge、action添加到状态机
        :param uuid_task:
        :param n_order:
        :return:
        """
        with self.lock:
            try:
                self.uuid_task = uuid_task
                if not self.order:
                    self.order = n_order
                    # 添加所有的 node
                if self.order.orderId != n_order.orderId:
                    self.reset()
                else:
                    self.reset_part()
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
            except Exception as e:
                self.log.error(f"[OrderStateMachine]add_order{e}")

    def del_node(self, ids: str):
        if ids in self.nodes:
            self.nodes.pop(ids)
            self.log.info(f"del_node :{ids}")

    def del_edge(self, ids: str):
        edge = self.edges.get(ids,None)
        if edge:
            self.del_node(edge.startNodeId)
            self.del_node(edge.endNodeId)
            self.edges.pop(ids)
            self.log.warning(f"del_edge :{ids}")
        # else:
        #     self.log.error(f"del_edge but not exist id {ids}")

    def del_action(self, ids: str):
        self.actions.pop(ids)

    def set_action_status(self, ids: str, status: Status):
        if self.actions.get(ids, None):
            self.actions[ids].actionStatus = status
            self.log.info(f"改变 action 状态:{status} ok！,actionId：{ids}")
        else:
            self.log.error(f"当准备改变 action 状态时，找不到对应的 actionId：{ids}")

    def set_instant_action_status(self, ids: str, status: Status):
        if self.instant_actions.get(ids, None):
            self.instant_actions[ids].actionStatus = status
        else:
            self.log.error(f"当准备改变 instant action 状态时，找不到对应的 actionId：{ids}")

    @property
    def actions_empty(self):
        try:
            if not self.actions:
                return True
            for ids, action in self.actions.items():
                if action.actionStatus != state.ActionStatus.FINISHED:
                    # 排除 instant_action  的任务
                    if action.actionType in action_type.instant_action_type:
                        return False
            return True
        except Exception as e:
            self.log.error(f"[OrderStateMachine]actions_empty error:{e}")

    @property
    def edges_empty(self):
        try:
            for ids, edge in self.edges.items():
                if not self.edges:
                    return True
                if edge.released:
                    return False
            return True
        except Exception as e:
            self.log.error(f"[OrderStateMachine]edges_empty error:{e}")

    @property
    def nodes_empty(self):
        try:
            if not self.nodes:
                return True
            for ids, node in self.nodes.items():
                if node.released:
                    return False
            return True
        except Exception as e:
            self.log.error(f"[OrderStateMachine]nodes_empty error:{e}")

    def get_order_status(self):
        with self.lock:
            return self.nodes, self.edges, self.actions, self.instant_actions

    def update_order_status(self, task_pack_status: pushMsgType.TaskStatusPackage, taskStatus: int):
        with self.lock:
            try:
                if not self.uuid_task and not self.instant_actions:
                    # self.log.info(f"task empty!!!")
                    return
                actions_empty = self.actions_empty
                if not actions_empty:
                    self.log.info(f"actions_empty")
                if not self.edges and actions_empty and not self.instant_actions:
                    return
                self.task_pack_status = task_pack_status
                self.taskStatus = taskStatus
                # self.log.info(f"taskStatus:{self.taskStatus},task_pack_status:{self.task_pack_status}")
                # 判断是否需要更新
                # 先判断 instant_actions 动作状态
                # 更新 instant action
                """taskStatus
                number	0 = NONE, 
                        1 = WAITING(目前不可能出现该状态), 
                        2 = RUNNING, 
                        3 = SUSPENDED, 
                        4 = COMPLETED, 
                        5 = FAILED, 
                        6 = CANCELED
                """
                if self.instant_actions:
                    for instant_action_id, instant_action in self.instant_actions.items():
                        if instant_action.actionType == 'cancelOrder':
                            if taskStatus == 6:
                                instant_action.actionStatus = Status.FINISHED
                            else:
                                instant_action.actionStatus = Status.FAILED
                        elif instant_action.actionType == 'startPause':
                            if taskStatus == 3:
                                instant_action.actionStatus = Status.FINISHED
                            else:
                                instant_action.actionStatus = Status.FAILED
                        elif instant_action.actionType == 'stopPause':
                            if taskStatus != 3:
                                instant_action.actionStatus = Status.FINISHED
                            else:
                                instant_action.actionStatus = Status.FAILED
                        elif instant_action.actionType == 'initPosition':
                            task_statu = next((task for task in task_pack_status.task_status_list if
                                               task.task_id == instant_action_id), None)
                            if task_statu:
                                self.update_instant_actions_status(instant_action_id, task_statu.status)
                        elif instant_action.actionType == 'Script':
                            task_statu = next((task for task in task_pack_status.task_status_list if
                                               task.task_id == instant_action_id), None)
                            if task_statu:
                                self.update_instant_actions_status(instant_action_id, task_statu.status)

                # 更新 edge 和 node
                need_del_edge_id = []
                try:
                    # 检查 node 或者 edge 为空的情况
                    if actions_empty and len(self.edges) == 0:
                        if self.nodes and len(self.edges) == 0:
                            self.nodes.clear()
                        if self.edges and len(self.nodes) == 0:
                            self.edges.clear()
                    for e_id,u_id in self.uuid_task.items():
                        get_edge = self.edges.get(e_id,None)

                        if get_edge:
                            self.log.info(f"get edge ok!!! edge id({e_id}):{get_edge}")
                            start_node = self.nodes.get(get_edge.startNodeId)
                            end_node = self.nodes.get(get_edge.endNodeId)
                            action_in_edge = None
                            if get_edge.actions:
                                action_in_edge = get_edge.actions[0]  # 只允许一个动作
                            for task_statu in task_pack_status.task_status_list:
                                # self.log.info(f"edgeId:{e_id},edgeTaskId:{u_id},task_statu.task_id:{task_statu.task_id}")
                                if task_statu.task_id == u_id:
                                    if task_statu.status == RobotOrderStatus.Completed.value:
                                        if action_in_edge:
                                            self.set_action_status(action_in_edge.actionId, Status.FINISHED)
                                        need_del_edge_id.append(e_id)
                                    elif task_statu.status == RobotOrderStatus.Failed.value and action_in_edge:
                                        self.set_action_status(action_in_edge.actionId, Status.FAILED)
                                    elif task_statu.status == RobotOrderStatus.StatusNone.value and action_in_edge:
                                        self.set_action_status(action_in_edge.actionId, Status.INITIALIZING)
                                    elif task_statu.status == RobotOrderStatus.Running.value and action_in_edge:
                                        self.set_action_status(action_in_edge.actionId, Status.RUNNING)
                                    elif task_statu.status == RobotOrderStatus.Canceled.value and action_in_edge:
                                        self.set_action_status(action_in_edge.actionId, Status.FAILED)
                                    elif task_statu.status == RobotOrderStatus.Suspended.value and action_in_edge:
                                        self.set_action_status(action_in_edge.actionId, Status.PAUSED)
                                    elif task_statu.status == RobotOrderStatus.NotFound.value and action_in_edge:
                                        self.set_action_status(action_in_edge.actionId, Status.FAILED)
                                    elif task_statu.status == RobotOrderStatus.Waiting.value and action_in_edge:
                                        self.set_action_status(action_in_edge.actionId, Status.WAITING)
                                    # else:
                                    #     self.log.warning(f"更新状态机 action 的状态时，找不到状态：{task_statu.status}")

                        if not actions_empty:
                            a = self.actions.get(e_id)
                            # 这里获取的都是 node 的 action
                            if a:
                                if task_statu.status == RobotOrderStatus.Completed:
                                    self.set_action_status(a.actionId, Status.FINISHED)
                                elif task_statu.status == RobotOrderStatus.Failed:
                                    self.set_action_status(a.actionId, Status.FAILED)
                                elif task_statu.status == RobotOrderStatus.StatusNone:
                                    self.set_action_status(a.actionId, Status.INITIALIZING)
                                elif task_statu.status == RobotOrderStatus.Running:
                                    self.set_action_status(a.actionId, Status.RUNNING)
                                elif task_statu.status == RobotOrderStatus.Canceled:
                                    self.set_action_status(a.actionId, Status.FAILED)
                                elif task_statu.status == RobotOrderStatus.Suspended:
                                    self.set_action_status(a.actionId, Status.PAUSED)
                                elif task_statu.status == RobotOrderStatus.NotFound:
                                    self.set_action_status(a.actionId, Status.FAILED)
                                elif task_statu.status == RobotOrderStatus.Waiting:
                                    self.set_action_status(a.actionId, Status.WAITING)
                                else:
                                    self.log.warning(f"更新状态机 action 的状态时，找不到状态：{task_statu.status}")
                    # self.log.info(f"need_del_edge_id:{need_del_edge_id}")
                except Exception as e:

                    self.log.error(f"[OrderStateMachine]uuid_task.items{e}")
                for del_edge_id in need_del_edge_id:

                    self.del_edge(del_edge_id)

            except Exception as e:
                self.log.error(f"[OrderStateMachine]update order status{e}")

    def update_instant_actions_status(self, ids, status):
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

    def reset(self):
        self.actions.clear()
        self.nodes.clear()
        self.edges.clear()
        self.instant_actions.clear()

    def set_cancel_status(self):

        self._set_actions_status_failed()

    def reset_part(self):
        self.instant_actions.clear()

    def _set_actions_status_failed(self):
        with self.lock:
            self.uuid_task = {}
            self.nodes.clear()
            self.edges.clear()
            if self.actions:
                for _,a in self.actions.items():
                    a.actionStatus = state.ActionStatus.FAILED

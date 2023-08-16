import asyncio
import copy
import datetime
import threading
from serve.OrderStateMachine import OrderStateMachine
from type import state, order, instantActions, connection, visualization
from typing import List, Union
import time
from serve.robot import Robot as Robot
from serve.mode import PackMode
from action_type.action_type import ActionPack, ActionType
from error_type import error_type as err
from type.RobotOrderStatus import Status


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"{func.__name__} start init")
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} start {(end - start) / 60:.6f}min")
        return result

    return wrapper


def send_order_decorator(func):
    def wrapper(self, task_list):
        self.logs.info(f"[state] decorator by send order")
        func(self, task_list)
        # 在执行完成后调用 _enqueue 方法
        self._enqueue(self.p_state, self.state)
        self.logs.info(f"[state]enqueue:{self.state.dict().__len__}")

    return wrapper


# 定义装饰器函数
def lock_decorator(func):
    # 创建锁对象
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        # 获取锁
        with lock:
            # 在加锁范围内执行方法
            return func(*args, **kwargs)

    # 返回装饰后的方法
    return wrapper


@timeit
class RobotOrder:

    def __init__(self, logs, loop=None, mode=PackMode.binTask):
        self.init = False
        self._event_loop = asyncio.get_event_loop() if loop is None else loop
        self.robot: Robot = Robot(logs)
        self.lock_order = threading.Lock()

        self.p_state: asyncio.Queue[state.State] = asyncio.Queue()
        self.s_order: asyncio.Queue[order.Order] = asyncio.Queue()
        self.p_connection: asyncio.Queue[connection.Connection] = asyncio.Queue()
        self.p_visualization: asyncio.Queue[visualization.Visualization] = asyncio.Queue()
        self.chanel_state: asyncio.Queue[state.State] = asyncio.Queue()
        # self.order_cache_queue: asyncio.Queue[dict] = asyncio.Queue()
        self.order = None
        self.current_order = None
        self.current_order_state: state.State = state.State.create_state()
        self.connection: connection.Connection = connection.Connection.create()
        self.robot_state_header_id = 0
        self.robot_connection_header_id = 0
        self.logs = logs
        self.state = state.State.create_state()
        self.init = False  # 表示第一次运行，用于判断运单逻辑
        self.order_task_list = list()
        self.robot_state_thread = threading.Thread(group=loop, target=self.handle_state, name="run robot state")
        self.robot_connection_thread = threading.Thread(group=None, target=self.handle_connection, name="run robot "
                                                                                                        "connect")
        self.robot_run_thread = threading.Thread(group=None, target=self.robot.run, name="run robot")
        self.mode = mode  # 定义动作模式 False为参数，True为binTask
        # 訂單狀態機
        self.order_state_machine = OrderStateMachine()

    def __del__(self):
        self._cls()

    async def run(self):
        self._run()

    def _run(self):
        # 拉取机器人状态，更新state
        self.robot_run_thread.start()
        # 上报state逻辑
        self.robot_state_thread.start()
        # topic connection
        self.robot_connection_thread.start()
        asyncio.gather(self.handle_order(), self.handle_report())

    async def handle_order(self):
        """
            订单统一入口
        """
        while True:
            self.logs.info("waiting order........")
            o = await self.s_order.get()
            self._run_order(o)

    async def handle_report(self):
        """
            发布 state 统一入口
        """
        while True:
            state_sub = await self.chanel_state.get()
            self._enqueue(self.p_state, state_sub)

    # async def handle_send_order_to_robot(self):
    #     """
    #         这里是最终将任务发给机器人执行入口
    #     """
    #     while True:
    #         task_list = await self.order_cache_queue.get()
    #         if self.robot.robot_online:
    #             self.send_order(task_list)
    #         else:
    #             """
    #               当机器人不在线时，需要做的逻辑，这里直接将任务丢弃
    #             """
    #             self.logs.info(f"robot not online,order pass and order detail:{task_list}")

    def update_state_loop(self):
        while True:
            time.sleep(2)
            print("-=" * 20)
            try:
                self.update_state_by_order()
            except Exception as e:
                print("更新任务状态出错：", e)

    def update_state_by_order(self):
        if not self.robot.robot_online:
            return
        try:
            if self.order_state_machine.edges_and_actions_id_list:
                self.order_state_machine.update_order_status(
                    self.robot.get_task_status(
                        self.order_state_machine.edges_and_actions_id_list))
                self.order_state_machine.update_state(self.robot.state)
        except Exception as e:
            print("狀態機 error",e)

    def handle_connection(self):
        while True:
            self.connection.connectionState = "ONLINE" if self.connection_online else ""
            self.connection.headerId = self.connection_header_id
            self.connection.timestamp = datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z'
            self._enqueue(self.p_connection, self.connection)
            time.sleep(60 * 10)

    def handle_visualization(self, task_status):
        while True:
            pass

    @property
    def connection_online(self) -> bool:
        """
           这里是上报 connection topic 是否在线逻辑，根据实际添加逻辑即可
        :return:
        """
        online = False
        if self.robot.robot_online:
            online = True
        return online

    def handle_instantActions(self, instant: instantActions.InstantActions):
        self.logs.info("handle_instantActions")
        actions = instant.instantActions
        for action in actions:
            # action_id = action.actionId
            action_type = action.actionType
            if action_type == "startPause":
                self.instant_start_pause()
            elif action_type == "stopPause":
                self.instant_stop_pause()
            elif action_type == "startCharging":
                # todo
                ActionPack.startCharging(action)
            elif action_type == "stopCharging":
                # todo
                ActionPack.stopCharging(action)
            elif action_type == "initPosition":
                # todo
                ActionPack.initPosition(action)
            elif action_type == "stateRequest":
                # todo
                ActionPack.stateRequest(action)
            elif action_type == "logReport":
                # todo
                ActionPack.logReport(action)
            elif action_type == "cancelOrder":
                print("cancelOrder 收到指令")
                self.instant_cancel_task()
            elif action_type == "factsheetRequest":
                # todo
                ActionPack.factsheetRequest(action)
            else:
                # todo 上报数据
                self.logs.error(f"不支持动作类型：{action_type}")

    def instant_stop_pause(self):
        self.robot.instant_stop_pause()

    def instant_start_pause(self):
        self.robot.instant_start_pause()

    def instant_cancel_task(self):
        self.robot.instant_cancel_task()
        self._cls()

    def _cls(self):
        self.s_order = asyncio.Queue()
        self.p_state = asyncio.Queue()
        self.chanel_state = asyncio.Queue()
        self.order = None
        self.current_order = None
        # 清除狀態機狀態
        self.order_state_machine.clear()

    def handle_state(self):
        """
        Events that trigger the transmission of the state message are:

        Receiving an order               √
        Receiving an order update        √
        Changes in the load status
        Errors or warnings
        Driving over a node
        Switching the operating mode
        Change in the "driving" field
        Change in the nodeStates, edgeStates or actionStates
        Returns:

        """
        while True:
            try:
                self.report()
            except Exception as e:
                self.logs.error(f"[state]report state error:{e}")

    def report_state_current_order(self):
        self.update_state_by_order()
        self._enqueue(self.chanel_state, self.robot.state)

    def report(self):
        time.sleep(2)
        self.logs.info(
            f"order status:|"
            f"{self.chanel_state.qsize()}|{self.p_state.qsize()}|{self.s_order.qsize()}|"
            f"{self.p_connection.qsize()}|")

        if not self.robot.robot_online or not self.current_order:
            self.report_robot_not_online()
        elif self.current_order is not None:
            self.report_state_current_order()
        else:
            print("over")

    def report_robot_not_online(self):
        self.update_state_by_order()
        self._enqueue(self.chanel_state, self.robot.state)

    def _report_order_error(self, sub_order):
        self.logs.info("todo" + sub_order.orderId)
        print("更新订单的id太小，需要上报错误")
        # todo

    def report_error(self, typ: err.ErrorOrder):
        self.logs.error(f"error type : {typ}")
        if typ == err.ErrorOrder.newOrderIdButOrderRunning:
            pass
        elif typ == err.ErrorOrder.nodeAndEdgeNumErr:
            pass

    def _run_order(self, task: order.Order):
        self.logs.info("[order] rec and start")
        if self.order_state_machine.ready:
            # 初始化，直接创建订单
            self.logs.info(f"[order] init,creat order")
            self.current_order = order.Order.create_order(task)
            # 狀態機
            self.order_state_machine.init_order(order.Order.create_order(task))
            self.execute_order()
        else:
            # 判断机器人当前的订单Id和新的订单Id是否一致
            self.logs.info(f"[order] try creat order")
            if self.current_order.orderId != task.orderId:
                # 订单不一致，开始创建新订单逻辑
                if self.order_state_machine.orders.orders.status != Status.FINISHED:
                    self.report_error(err.ErrorOrder.newOrderIdButOrderRunning)
                else:
                    # 创建新的订单
                    self._try_create_order(task)
            else:
                # 订单一致，开始订单更新逻辑
                # orderUpdateId 比较
                if self.current_order.orderUpdateId <= task.orderUpdateId:
                    if self.current_order.orderUpdateId == task.orderUpdateId:
                        # 订单orderUpdateId已存在，丢弃信息
                        self.logs.info(f"orderUpdateId已存在，丢弃信息")
                    else:
                        if self.order_state_machine.orders.orders.status != Status.FINISHED:
                            """
                                机器人正在从1到10，在4的时候，order说，可以去115了，这个时候，需要更新订单 4-15
                            """
                            # 更新订单
                            # ------------------------------------------
                            #          重要节点
                            # ------------------------------------------
                            self._try_update_order(task)
                        else:
                            """
                                机器人正在从1到10，已经在10了，在等order，然后order说，可以去15了，这个时候，需要更新订单 10-15
                            """
                            # 创建新的订单
                            self._try_update_order(task)
                else:
                    # orderUpdateId 错误，上报错误，拒绝订单
                    self.report_error(err.ErrorOrder.orderUpdateIdLowerErr)

    def _try_create_order(self, sub_order):
        print("收到新的orderId，并且当前没有任务，尝试创建新的订单。。。")
        self.order = order.Order.create_order(sub_order)

        self.lock_order.acquire()
        self.current_order = self.order
        self.order_state_machine.init_order(self.current_order)
        self.lock_order.release()
        # self.logs.info(self.order.nodes)
        # self.logs.info(self.order.nodes)
        self.execute_order()

    def _try_update_order(self, sub_order):
        """
        用于更新订单，收到更新订单的任务，将新order和旧order拼接比较
        :param sub_order:
        :return:
        """

        print("尝试更新订单")
        flag = self.is_match_node_start_end(sub_order.nodes, self.current_order.nodes)
        if flag:
            # self.current_order = sub_order
            self.current_order.orderUpdateId = sub_order.orderUpdateId
            self.update_order(sub_order)
        else:
            print("node and edge errors")
            self._report_order_error(sub_order)

    def update_order(self, sub_order: order.Order):
        update_order = order.Order.create_order(sub_order)

        # 狀態機

        self.order_state_machine.update_order(update_order)

        update_nodes = []
        update_edges = []
        for u_n in update_order.nodes:
            update_nodes.append(u_n)
        for u_e in update_order.edges:
            update_edges.append(u_e)
        update_nodes, update_edges = self.check_nodes_edges(update_nodes, update_edges)
        if not update_nodes or not update_edges:
            self.report_error(err.ErrorOrder.nodeAndEdgeNumErr)
            return
        task_list = self.pack_tasks(update_nodes, update_edges)
        # self.order_enqueue(task_list=task_list)
        self.robot.send_order(task_list)

    @staticmethod
    def is_action_states_finished_empty(action_states) -> int:
        action_tack_len = 0
        if action_states is None:
            return action_tack_len
        for k, v in action_states.items():
            if v.actionStatus != state.ActionStatus.FINISHED:
                action_tack_len += 1
        return action_tack_len

    @staticmethod
    def is_nodes_empty(node_states: dict) -> int:
        node_task_len = 0
        if len(node_states.keys()) == 0:
            # print("len(node_states.keys()):",len(node_states.keys()),",node_states.keys():",node_states.keys())
            return node_task_len
        for node_state in node_states.values():
            # print("node_state:",node_state)
            if isinstance(node_state, state.NodeState):
                if node_state.released:
                    node_task_len += 1
        # print("判断节点是否为空", node_states)
        return node_task_len

    @staticmethod
    def is_edges_empty(edge_states: dict) -> int:
        edge_task_len = 0
        if len(edge_states.keys()) == 0:
            return edge_task_len
        for edge_state in edge_states.values():
            if isinstance(edge_state, state.EdgeState):
                # print("edge_state.released:",edge_state.released)
                if edge_state.released:
                    edge_task_len += 1
        # print("return:",edge_task_len)
        return edge_task_len

    @classmethod
    def is_match_node_start_end(cls, new_node: List[order.Node], old_node: List[order.Node]) -> bool:
        """"
        校对 new base 和 old base 的 node 是否一致
        情况1：
            旧：1 1 1 0 0 0
            新：    1 1 0 0   return True
        情况2：
            旧：1 1 1 0 0 0
            新：      1 0 0   return False
        情况3：
            旧：1 1 1 1 1 1
            新：      1 0 0   return False
        :return bool
        """
        # todo
        if not (isinstance(new_node, list) or isinstance(old_node, list)) or len(new_node) == 0 or len(old_node) == 0:
            print(f"new_node:{type(new_node)},{new_node}\n")
            print(f"old_node:{type(old_node)},{old_node}\n")
            print("校对 new base 和 old base 的 node 是否一致时，输入节点类型不是节点,或者 list 为空")
            return False
        end = None
        start = new_node[0]
        if not start.released:
            print(f"输入的第一个节点的 base 为 {start.released}")
            return False
        for i, node in enumerate(old_node):
            if node.released is True:
                if len(old_node) == i + 1:
                    end = old_node[i]
                    break
                if old_node[i + 1].released is False:
                    end = old_node[i]
                    print(i, end)
                    break
        if end is not None and start:
            if end.nodeId == start.nodeId and end.sequenceId == start.sequenceId:
                return True
            else:
                print(f"nodeId:{end.nodeId} 与 {start.nodeId},\nsequenceId:{end.sequenceId} 与 {start.sequenceId}")
                return False
        return False

    def _enqueue(self, q, obj):
        asyncio.run_coroutine_threadsafe(q.put(obj), self._event_loop)

    def execute_order(self):
        """
            打包任务，发给机器人,只是将 node 和 edge 处理打包成 3066 的任务格式，发给机器人
        :return:None
        """

        try:
            edges = self.current_order.edges
            nodes = self.current_order.nodes
            # self.logs.info(f"排序前的：{nodes}")
            nodes, edges = self.check_nodes_edges(nodes, edges)
            if not nodes:
                self.report_error(err.ErrorOrder.nodeAndEdgeNumErr)
                return
            task_list = self.pack_tasks(nodes, edges)
            # self.order_enqueue(task_list=task_list)
            # todo
            self.robot.send_order(task_list)
        except Exception as e:
            self.logs.info(f"试图打包任务，发给机器人 失败:{e}")
            self.report_error(err.ErrorOrder.sendOrderToRobotErr)

    @staticmethod
    def check_nodes_edges(nodes, edges):
        if (len(nodes) - 1) == len(edges):
            # print("nodes -1 len == edges len")
            nodes.sort(key=lambda x: x.dict()["sequenceId"])
            edges.sort(key=lambda y: y.dict()["sequenceId"])
            # print("nodes -1 len != edges len")
            return nodes, edges
        return [], []

    @lock_decorator
    def pack_tasks(self, nodes: List[order.Node], edges: List[order.Edge]):
        """
        根据 self.mode 打包任务
        1、node 和 edge 分开打包
        2、第一个点不打包
        3、

        """
        if not nodes or not edges:
            self.report_error(err.ErrorOrder.nodeOrEdgeEmpty)
            return []
        nodes_edges_lists = self.pack_nodes_edges_list(nodes, edges)
        if not nodes_edges_lists:
            self.report_error(err.ErrorOrder.packNodeEdgeListErr)
            return []
        task_list = []

        nodes_point = dict()
        if self.mode != PackMode.vda5050:
            if not self.robot.map_manager.map_point_index:
                self.logs.error(f"read map point but empty while packing tasks")
                return []
            nodes_point = {
                node.nodeId: self.robot.map_manager.map_point_index.get((node.nodePosition.x, node.nodePosition.y)) for
                node in
                nodes}
            print(nodes_point)

        for i_p, point in enumerate(nodes_edges_lists):
            if isinstance(point, order.Node):
                # print("node")
                # 在地图中找一个点，匹配node的坐标点
                if self.mode != PackMode.vda5050:
                    p = nodes_point.get(point.nodeId)
                    if p:
                        self.pack_node(point, task_list)
                elif self.mode == PackMode.vda5050:
                    self.pack_node(point, task_list)
            elif isinstance(point, order.Edge):
                if self.mode != PackMode.vda5050:
                    edge_start_point = nodes_point.get(point.startNodeId)
                    edge_end_point = nodes_point.get(point.endNodeId)
                    if not edge_start_point or not edge_end_point:
                        self.report_error(err.ErrorOrder.packTaskEdgeErr)
                        return []
                    self.pack_edge(point, task_list, edge_start_point, edge_end_point)
                elif self.mode == PackMode.vda5050:
                    self.pack_edge(point, task_list)
            else:
                self.logs.error(f"pack_tasks:unknown msg")
        return task_list

    def pack_node(self, node: order.Node, task_list: list):
        # 节点不会下发任务给机器人
        # 创建节点
        if node.actions:
            self.pack_actions(node, task_list)

    def pack_edge(self, edge: order.Edge, task_list: list, edge_start_point=None, edge_end_point=None):
        if edge_start_point and edge_end_point:
            edge_task = {
                "task_id": edge.edgeId,
                "id": edge_end_point,
                "source_id": edge_start_point,
                "operation": "Wait",
                "percentage": 1.0
            }
            if edge.actions is None:
                edge_task["reach_angle"] = 3.141592653589793
            if edge.released:
                task_list.append(edge_task)
            if edge.actions:
                self.pack_actions(edge, task_list, edge_task)

    def pack_actions(self, NE: Union[order.Node, order.Edge], task_list: list, task=None):
        actions = NE.actions
        for action in actions:
            action_task = dict()
            if action.actionType == ActionType.PICK:
                action_task = ActionPack.pick(action, self.mode)
            elif action.actionType == ActionType.DROP:
                action_task = ActionPack.drop(action, self.mode)

            if not action_task:
                print("action_task error:", action_task)
                return
            if task:
                task["script_name"] = action_task["script_name"]
                task["script_args"] = action_task["script_args"]
                task["operation"] = action_task["operation"]
                task["script_stage"] = 1
                action_task = task
            if NE.released:
                task_list.append(action_task)

    @classmethod
    def pack_nodes_edges_list(cls, nodes: List[order.Node], edges: List[order.Edge]):
        """
        将 node 和 edge 的任务打包在一起
        :param nodes:
        :param edges:
        :return:list
        """
        nodes_copy = copy.deepcopy(nodes)
        edges_copy = copy.deepcopy(edges)
        nodes_edges_list = []
        while nodes_copy and edges_copy:
            node = nodes_copy.pop(0)
            nodes_edges_list.append(node)
            edge = edges_copy.pop(0)
            if edge.startNodeId != node.nodeId:
                return []
            nodes_edges_list.append(edge)
            if str(edge.endNodeId) != str(nodes_copy[0].nodeId):
                return []
            if not edges_copy and nodes_copy:
                nodes_edges_list.append(nodes_copy[-1])
        return nodes_edges_list[1:]

    # def order_enqueue(self, task_list, type_id=3066):
    #     """
    #         任务入队
    #     """
    #     self._enqueue(self.order_cache_queue, task_list)

    # @send_order_decorator
    # def send_order(self, task_list):
    #     self.robot.send_order(task_list)

    # @send_order_decorator
    # def send_order(self, task_list, type_id=3066):
    #     if not isinstance(task_list, list):
    #         self.logs.error("send_order is empty:", task_list)
    #         return
    #     move_task_list = {
    #         'move_task_list': task_list
    #     }
    #     flag = True
    #     try:
    #         while flag:
    #             if self.robot.lock:
    #                 _, res_data = self.robot.rbk.request(type_id, msg=move_task_list)
    #                 res_data_json = json.loads(res_data)
    #                 self.logs.info(f"下发任务内容：{move_task_list}, rbk 返回结果：{res_data_json}")
    #                 if res_data_json["ret_code"] == 0:
    #                     self.logs.info(f"下发任务成功：{move_task_list}")
    #                     flag = False
    #                 else:
    #                     self.logs.info(f"下发任务失败：{move_task_list}")
    #
    #             else:
    #                 self.logs.info("没有控制权，无法下发任务")
    #     except Exception.args as e:
    #         self.logs.info("试图抢占控制权并下发任务失败，可能是没有链接到机器人" + e)

    @property
    def state_header_id(self):
        self.robot_state_header_id += 1
        return self.robot_state_header_id

    def undate_header(self):
        self.state.orderId = self.current_order.orderId
        self.state.orderUpdateId = self.current_order.orderUpdateId
        self.state.headerId = self.state_header_id
        self.state.timestamp = datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z'

    @property
    def connection_header_id(self):
        self.robot_connection_header_id += 1
        return self.robot_connection_header_id

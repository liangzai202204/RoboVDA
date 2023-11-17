import asyncio
import datetime
import threading
from serve.OrderStateMachine import OrderStateMachine
from serve.topicQueue import TopicQueue
from type import state, order, instantActions, connection, visualization, RobotOrderStatus
from typing import List, Union
import time
from serve.robot import Robot as Robot
from action_type.action_type import ActionPack
from error_type import error_type as err
from type.RobotOrderStatus import Status
from serve.packTask import PackTask
from log.log import MyLogger


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


class HandleTopic:

    def __init__(self, robot: Robot, mode, loop=None, state_report_frequency=1, robot_type=1):
        self.state_report_frequency = state_report_frequency
        self.init = False
        self._event_loop = asyncio.get_event_loop() if loop is None else loop
        self.robot: Robot = robot
        self.lock_order = threading.Lock()
        self.robot_type = robot_type
        self.order = None
        self.current_order = None
        # 用於保存協議層面的 error，錯誤產生的時候存放，在新的訂單來臨時清空。區別於在 robot.py 的 update errors（來自於機器人的錯誤）
        self.state_error = []
        self.current_order_state: state.State = state.State.create_state()
        self.connection: connection.Connection = connection.Connection.create()
        self.visualization: visualization.Visualization = visualization.Visualization.create()
        self.robot_state_header_id = 0
        self.robot_connection_header_id = 0
        self.robot_visualization_header_id = 0
        self.logs = MyLogger()
        self.state = state.State.create_state()
        self.init = False  # 表示第一次运行，用于判断运单逻辑
        self.mode = mode  # 定义动作模式 False为参数，True为binTask
        # 訂單狀態機
        self.order_state_machine = OrderStateMachine()
        self.pack_task = PackTask(mode, self.robot.map_manager.map_point_index, robot_type)

    def __del__(self):
        self._cls()

    async def run(self):

        await self._run()

    async def _run(self):
        await asyncio.gather(self.handle_order(),
                             self.handle_state(),
                             self.handle_instantActions(),
                             self.handle_connection(),
                             self.handle_visualization(),
                             self.handle_state_report()
                             )

    async def handle_order(self):
        """
            订单统一入口
        """
        while True:
            self.logs.info("waiting order........")
            o = await TopicQueue.s_order.get()
            self._run_order(o)

    async def handle_instantActions(self):
        """
            订单统一入口
        """
        while True:
            self.logs.info("handle_instantActions ........")
            instantAction = await TopicQueue.s_instantActions.get()
            self._handle_instantActions(instantAction)

    async def handle_state(self):
        """
            发布 state 统一入口
        """
        while True:
            state_sub = await TopicQueue.chanel_state.get()
            await self._enqueue(TopicQueue.p_state, state_sub)

    def update_state_by_order_state_machine(self):
        if not self.robot.robot_online:
            return
        try:
            if self.order_state_machine.edges_and_actions_id_list:
                self.order_state_machine.update_order_status(
                    self.robot.get_task_status(
                        self.order_state_machine.edges_and_actions_id_list))
            self.order_state_machine.update_state(self.robot.state)
        except Exception as e:
            self.logs.error(f"狀態機 error:{e}")

    async def handle_connection(self):
        while True:
            self.connection.connectionState = "ONLINE" if self.connection_online else ""
            self.connection.headerId = self.connection_header_id
            self.connection.timestamp = datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z'
            await self._enqueue(TopicQueue.p_connection, self.connection)
            await asyncio.sleep(10)

    async def handle_visualization(self):
        while True:

            try:
                self.visualization.agvPosition = self.robot.state.agvPosition
                self.visualization.velocity = self.robot.state.velocity
                self.visualization.headerId = self.visualization_header_id
                self.visualization.timestamp = datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z'
                await self._enqueue(TopicQueue.p_visualization, self.visualization)
                await asyncio.sleep(10)
            except Exception as e:
                self.logs.error(f"handle_visualization error:{e}")
                await asyncio.sleep(10)

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

    def _handle_instantActions(self, instant: instantActions.InstantActions):
        self.logs.info("handle_instantActions")
        actions = instant.actions
        for action in actions:
            # action_id = action.actionId
            action_type = action.actionType
            if action_type == "startPause":
                self.instant_start_pause(action)
            elif action_type == "stopPause":
                self.instant_stop_pause(action)
            elif action_type == "startCharging":
                # todo
                ActionPack.startCharging(action)
            elif action_type == "stopCharging":
                # todo
                ActionPack.stopCharging(action)
            elif action_type == "initPosition":
                self.instant_initPosition(ActionPack.initPosition(action))
            elif action_type == "stateRequest":
                # todo
                ActionPack.stateRequest(action)
            elif action_type == "logReport":
                # todo
                ActionPack.logReport(action)
            elif action_type == "cancelOrder":
                print("cancelOrder 收到指令")
                self.instant_cancel_task(action)
            elif action_type == "factsheetRequest":
                # todo
                ActionPack.factsheetRequest(action)
            else:
                # todo 上报数据
                self.logs.error(f"不支持动作类型：{action_type}")

    def instant_stop_pause(self,action: order.Action):
        try:
            self.robot.instant_stop_pause()
            self.logs.info(f'instant_stop_pause ok!')
            self.order_state_machine.set_stop_pause_instant_action(action, Status.FINISHED)
        except Exception as e:
            self.logs.error(f"set_stop_pause_instant_action error:{e}")
            self.order_state_machine.set_stop_pause_instant_action(action, Status.FAILED)

    def instant_start_pause(self,action: order.Action):
        try:
            self.robot.instant_start_pause()
            self.logs.info(f'instant_start_pause ok!')
            self.order_state_machine.set_start_pause_instant_action(action, Status.FINISHED)
        except Exception as e:
            self.logs.error(f"set_start_pause_instant_action error:{e}")
            self.order_state_machine.set_start_pause_instant_action(action, Status.FAILED)



    def instant_cancel_task(self, action: order.Action):
        """取消任务逻辑
        1、有任务直接取消
            已经执行的 action 状态保持不变，未执行的将状态改为 FAILED。
            同时将 cancel_order action 的 状态添加到 actionState中。
        2、没有任务，需要上报错误
            上报错误是将错误信息添加到 state.errors 中，
            {
                "errorType": "noOrderToCancel",
                "errorLevel": "WARNING",
                "errorReferences": "这里是 actionId",
                "errorDescription": ""
            }
            在新的订单来临时，清楚错误
        :param action:
        :return:
        """
        try:
            if self.order_state_machine.cancel_order or not self.order_state_machine.task_id_list:
                self.state_error.append(state.Error(**{
                    "errorType": "noOrderToCancel",
                    "errorLevel": "WARNING",
                    "errorReferences": [state.ErrorReference(**{
                        "referenceKey":"actionId",
                        "referenceValue":action.actionId
                    })],
                    "errorDescription": ""
                }))
                self.order_state_machine.set_cancel_order_instant_action(action, Status.FINISHED)
                self.logs.error(f"[instantAction]noOrderToCancel:{self.state_error}")

                return
            if self.robot.instant_cancel_task():
                self.order_state_machine.set_cancel_order_instant_action(action, Status.FINISHED)
            else:
                self.order_state_machine.set_cancel_order_instant_action(action, Status.FAILED)
        except Exception as e:
            self.logs.error(f"set_cancel_order_instant_action error:{e}")

    def instant_initPosition(self, task):
        self.robot.instant_init_position(task)

    def _cls(self):
        self.order = None
        self.current_order = None
        self.robot.state.nodeStates = []
        self.robot.state.edgeStates = []
        # 清除狀態機狀態
        self.order_state_machine.clear()

    async def handle_state_report(self):
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
                await asyncio.sleep(self.state_report_frequency)
                self.logs.info(
                    f"TopicQueue status:|"
                    f"{TopicQueue.chanel_state.qsize()}|"
                    f"{TopicQueue.p_state.qsize()}|"
                    f"{TopicQueue.p_connection.qsize()}|"
                    f"{TopicQueue.p_visualization.qsize()}|"
                    f"{TopicQueue.s_order.qsize()}|"
                    f"{TopicQueue.s_instantActions.qsize()}|"
                    f"{TopicQueue.pushData.qsize()}|"
                )

                await self.report_state_by_current_order()
            except Exception as e:
                self.logs.error(f"[state]report state error:{e}")

    async def report_state_by_current_order(self):
        self.update_state_by_order_state_machine()
        if self.current_order:
            self.robot.state.orderId = self.current_order.orderId
            self.robot.state.orderUpdateId = self.current_order.orderUpdateId
        self.robot.state.errors.clear()
        if self.state_error:
            # 如有error 則添加到 state 中
            for s_e in self.state_error:
                self.robot.state.errors.append(s_e)
        if self.robot.robot_online:
            self.robot.state.errors.extend(self.robot.update_errors())
        await self._enqueue(TopicQueue.chanel_state, self.robot.state)

    def _report_order_error(self, sub_order):
        self.logs.info("todo" + sub_order.orderId)
        print("更新订单的id太小，需要上报错误")
        # todo

    def report_error(self, typ: err.ErrorOrder):
        # TODO 上报错误逻辑
        self.logs.error(f"error type : {typ}")
        if typ == err.ErrorOrder.newOrderIdButOrderRunning:
            pass
        elif typ == err.ErrorOrder.nodeAndEdgeNumErr:
            pass

    def _run_order(self, task: order.Order):
        self.logs.info("[order] rec and start")
        with self.lock_order:
            # 有新的 order , 清空 state error
            self.state_error.clear()
            if self.order_state_machine.ready:
                # 初始化，直接创建订单
                self.logs.info(f"[order] init,creat order")
                self.current_order = order.Order.create_order(task)
                # 狀態機
                self.order_state_machine.init_order(self.current_order)
                self.execute_order()
                return
            # 判断机器人当前的订单Id和新的订单Id是否一致
            self.logs.info(f"[order] try creat order")
            if self.current_order.orderId != task.orderId:
                # 订单不一致，开始创建新订单逻辑
                if self.order_state_machine.orders.orders.status != Status.FINISHED:
                    self.report_error(err.ErrorOrder.newOrderIdButOrderRunning)
                else:
                    # 创建新的订单
                    self._try_create_order(task)
                return
            # 订单一致，开始订单更新逻辑
            # orderUpdateId 比较
            if self.current_order.orderUpdateId <= task.orderUpdateId:
                if self.current_order.orderUpdateId == task.orderUpdateId:
                    # 订单orderUpdateId已存在，丢弃信息
                    self.logs.info(f"orderUpdateId已存在，丢弃信息")
                    return
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
                return
            # orderUpdateId 错误，上报错误，拒绝订单
            self.report_error(err.ErrorOrder.orderUpdateIdLowerErr)

    def _try_create_order(self, sub_order):
        print("收到新的orderId，并且当前没有任务，尝试创建新的订单。。。")
        self.order = order.Order.create_order(sub_order)

        self.current_order = self.order
        self.order_state_machine.init_order(self.current_order)
        # self.logs.info(self.order.nodes)
        # self.logs.info(self.order.nodes)
        self.execute_order()

    def _try_update_order(self, sub_order):
        """
        用于更新订单，收到更新订单的任务，将新order和旧order拼接比较
        :param sub_order:
        :return:
        """
        if self.is_match_node_start_end(sub_order.nodes, self.current_order.nodes):
            # self.current_order = sub_order
            self.current_order.orderUpdateId = sub_order.orderUpdateId
            self.update_order(sub_order)
            return
        print("node and edge errors")
        self._report_order_error(sub_order)

    def update_order(self, sub_order: order.Order):
        update_order = order.Order.create_order(sub_order)
        # 狀態機
        self.order_state_machine.update_order(update_order)
        self.pack_send(update_order)

    def pack_send(self, new_order: order.Order):
        res = self.pack_task.pack(new_order, self.robot.map_manager.map_point_index)
        if isinstance(res, err.ErrorOrder):
            self.report_error(res)
        elif isinstance(res, list) and res:
            self.robot.send_order(res)
        elif not res:
            self.report_error(err.ErrorOrder.sendOrderToRobotErr)

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
                    break
        for i, N_node in enumerate(new_node):
            if N_node.nodeId == end.nodeId and N_node.released == True:
                return True
        return False

    async def _enqueue(self, q: asyncio.Queue, obj):
        if q.full():
            await q.get()
        await q.put(obj)

    def execute_order(self):
        """
            打包任务，发给机器人,只是将 node 和 edge 处理打包成 3066 的任务格式，发给机器人
        :return:None
        """

        try:
            self.pack_send(self.current_order)
        except Exception as e:
            self.logs.info(f"试图打包任务，发给机器人 失败:{e}")
            self.report_error(err.ErrorOrder.sendOrderToRobotErr)

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

    @property
    def visualization_header_id(self):
        self.robot_visualization_header_id += 1
        return self.robot_visualization_header_id

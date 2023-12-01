import asyncio
import datetime
import threading
from src.serve.OrderStateMachine import OrderStateMachine
from src.serve.topicQueue import TopicQueue
from src.type.VDA5050 import state, order, factsheet, connection, instantActions, visualization
from typing import List
from src.serve.robot import Robot as Robot
from src.pack.action_type import ActionPack
from src.error import error_type as err
from src.type.RobotOrderStatus import Status
from src.pack.packTask import PackTask
from src.log.log import MyLogger
from src.config.config import Config
from src.sim.sim_order import SimOrder


class HandleTopic:

    def __init__(self, robot: Robot, config: Config):
        self.state_report_frequency = config.state_report_frequency
        self.robot_type = config.robot_type
        self.robot: Robot = robot
        self.sim_order = SimOrder(config, robot)
        self.lock_order = threading.Lock()
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
        # 訂單狀態機
        self.order_state_machine = OrderStateMachine()
        self.pack_task = PackTask(config)
        self.handle_actions = self._handle_actions()
        self.error_state = state.Error()

    def __del__(self):
        self._cls()

    async def run(self):
        while True:
            if self.robot.robot_online:
                await self._run()
            else:
                await asyncio.sleep(1)
                self.logs.warning(f"[HandleTopic]robot not on line ,waiting 1 s")

    async def _run(self):
        results = await asyncio.gather(self.handle_order(),
                                       self.handle_state(),
                                       self.handle_instantActions(),
                                       self.handle_connection(),
                                       self.handle_visualization(),
                                       self.handle_factsheet(),
                                       self.handle_state_report(),
                                       return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logs.error(f"Task {i} raised exception: {result}")
            else:
                self.logs.info(f"Task {i} succeeded with result: {result}")

    async def handle_order(self):
        """
            订单统一入口
        """
        while True:
            if self.robot.robot_online:
                self.logs.info("waiting order........")
                o = await TopicQueue.s_order.get()
                self._run_order(o)
            else:
                self.logs.info("robot not online........")

    async def handle_instantActions(self):
        """
            订单统一入口
        """
        while True:
            if self.robot.robot_online:
                self.logs.info("waiting handle_instantActions ........")
                instantAction = await TopicQueue.s_instantActions.get()
                self._handle_instantActions(instantAction)
            else:
                self.logs.info("robot not online........")

    async def handle_factsheet(self):
        """
            订单统一入口
        """
        while True:
            if self.robot.robot_online:
                self.logs.info("waiting handle_factsheet ........")
                factsheet = await TopicQueue.s_factSheet.get()
                self._handle_factsheet(factsheet)
            else:
                self.logs.info("robot not online........")

    async def handle_state(self):
        """
            发布 state 统一入口
        """
        while True:
            state_sub = await TopicQueue.chanel_state.get()
            await self._enqueue(TopicQueue.p_state, state_sub)

    def update_state_by_order_state_machine(self):
        try:
            self.order_state_machine.update_order_status(self.robot.robot_push_msg.task_status_package,
                                                         self.robot.robot_push_msg.task_status)
            nodes_s, edges_s, actions_s, instantActions_s = self.order_state_machine.get_order_status()
            self.robot.state.lastNodeId, self.robot.state.lastNodeSequenceId = self.order_state_machine.get_last_node()

            nodeState = []
            edgeState = []
            actionState = []
            instantActionState = []
            # 更新 state 的 nodeState
            for ids_n, n_s in nodes_s.items():
                nodeState.append(n_s)
                nodeState.sort(key=lambda x: x.sequenceId)
            # 更新 state 的 edgeState
            for ids_e, e_s in edges_s.items():
                edgeState.append(e_s)
                edgeState.sort(key=lambda x: x.sequenceId)
            # 更新 state 的 actionState
            for ids_a, a_s in actions_s.items():
                actionState.append(a_s)
            # 更新 state 的 actionState
            for ids_i, i_s in instantActions_s.items():
                instantActionState.append(i_s)
            self.robot.state.nodeStates.clear()
            self.robot.state.nodeStates.extend(nodeState)
            self.robot.state.edgeStates.clear()
            self.robot.state.edgeStates.extend(edgeState)
            self.robot.state.actionStates.clear()
            self.robot.state.actionStates.extend(actionState)
            self.robot.state.actionStates.extend(instantActionState)
            self.robot.state.newBaseRequest = True if len(self.robot.state.nodeStates) == 0 else False
        except Exception as e:
            self.logs.error(f"[state][update]:{e}")

    async def handle_connection(self):
        while True:
            self.connection.connectionState = "ONLINE" if self.connection_online else "OFFLINE"
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
        if self.robot.robot_online:
            return True
        return False

    def _handle_factsheet(self, f: factsheet.Factsheet):
        self.logs.info("_handle_factsheet")

    def _handle_instantActions(self, instant: instantActions.InstantActions):
        self.logs.info("handle_instantActions")
        actions = instant.actions
        print(actions)
        for action in actions:
            action_type = action.actionType
            handler = self.handle_actions.get(action_type)
            print(handler)
            if handler:
                handler(action)
            else:
                self.logs.error(f"[instantActions]不支持动作类型：{action_type}")

    def http_handle_instantActions(self, instant: instantActions.InstantActions):
        self._handle_instantActions(instant)

    def instant_stop_pause(self, action: order.Action):
        if self.robot.instant_stop_pause():
            self.order_state_machine.add_instant_action(action)
            self.logs.info(f'[instant_action]instant_start_pause ok!')
        else:
            self.order_state_machine.add_instant_action(action, Status.FAILED)

    def instant_start_pause(self, action: order.Action):
        if self.robot.instant_start_pause():
            self.order_state_machine.add_instant_action(action)
            self.logs.info(f'[instant_action]instant_start_pause ok!')
        else:
            self.order_state_machine.add_instant_action(action, Status.FAILED)

    def instant_script(self, action: order.Action):
        task = ActionPack.pack_action(action, 0)
        if self.robot.instant_init_position([task]):
            self.order_state_machine.add_instant_action(action)
            self.pack_task.task_pack_list.append(task)
            self.logs.info(f'[instant_action]instant_start_pause ok!')
        else:
            self.order_state_machine.add_instant_action(action, Status.FAILED)

    def instant_factsheet_request(self, action: order.Action):
        TopicQueue.s_factSheet.put(self.robot.factsheet)

        self.logs.info(f'[instant_action]instant_factsheet_request ok!')
        self.order_state_machine.add_instant_action(action, Status.FINISHED)

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
            if self.order_state_machine.is_order_empty():
                self.state_error.append(state.Error(**{
                    "errorType": "noOrderToCancel",
                    "errorLevel": "WARNING",
                    "errorReferences": [state.ErrorReference(**{
                        "referenceKey": "actionId",
                        "referenceValue": action.actionId
                    })],
                    "errorDescription": ""
                }))
                self.logs.error(f"[instantAction]noOrderToCancel:{self.state_error}")
                self.order_state_machine.add_instant_action(action, Status.FINISHED)
                return

            if self.robot.instant_cancel_task():
                self.order_state_machine.set_cancel_status(action)
            else:
                self.order_state_machine.set_cancel_status(action, Status.FAILED)
        except Exception as e:
            self.logs.error(f"set_cancel_order_instant_action error:{e}")

    def instant_initPosition(self, action):
        task = ActionPack.initPosition(action)
        if self.robot.instant_init_position(task):
            self.order_state_machine.add_instant_action(action)
            self.logs.info(f'[instant_action]instant_start_pause ok!')
        else:
            self.order_state_machine.add_instant_action(action, Status.FAILED)

    def _cls(self):
        self.current_order = None
        self.robot.state.nodeStates = []
        self.robot.state.edgeStates = []
        # 清除狀態機狀態
        self.order_state_machine.reset()

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
                # self.logs.info(
                #     f"TopicQueue status:|"
                #     f"{TopicQueue.chanel_state.qsize()}|"
                #     f"{TopicQueue.p_state.qsize()}|"
                #     f"{TopicQueue.p_connection.qsize()}|"
                #     f"{TopicQueue.p_visualization.qsize()}|"
                #     f"{TopicQueue.s_order.qsize()}|"
                #     f"{TopicQueue.s_instantActions.qsize()}|"
                #     f"{TopicQueue.pushData.qsize()}|"
                # )
                await self.report_state_by_current_order()
            except Exception as e:
                self.logs.error(f"[state]report state error:{e}")

    async def report_state_by_current_order(self):
        try:
            if self.current_order:
                self.robot.state.orderId = self.current_order.orderId
                self.robot.state.orderUpdateId = self.current_order.orderUpdateId
            # 更新错误，一种是机器人本身的错误，一种是本程序的错误
            self.robot.state.errors.clear()
            if self.state_error:
                # 如有error 則添加到 state 中
                for s_e in self.state_error:
                    self.robot.state.errors.append(s_e)
            if self.robot.robot_online:
                # 机器人错误
                self.robot.state.errors.extend(self.robot.update_errors())
            self.update_state_by_order_state_machine()
            await self._enqueue(TopicQueue.chanel_state, self.robot.state)
        except Exception as e:
            self.logs.error(f" update report_state_by_current_order error:{e}")

    def report_error(self, error_type: str, error_level: state.ErrorLevel,
                     reference_key:str, reference_value:str,error_description=""):
        """上报错误逻辑"""
        self.error_state.errorType = error_type
        self.error_state.errorLevel = error_level
        self.error_state.errorReferences = [
            state.ErrorReference(
                referenceKey=reference_key,
                referenceValue=reference_value
            )
        ]
        self.error_state.errorDescription = error_description
        self.state_error.append(self.error_state)
        self.logs.info(f"report_error ok!!!")

    def http_run_order(self, task: order.Order):
        self._run_order(task)

    def http_run_instant_actions(self, task: instantActions.InstantActions):
        self._handle_instantActions(task)

    def _run_order(self, task: order.Order):
        self.logs.info("[order] rec and start")
        with self.lock_order:
            try:
                # 有新的 order , 清空 state error
                self.state_error.clear()
                if not self.order_state_machine.order:
                    self.order_state_machine.reset()
                # is order_empty? by order_state_machine
                if self.order_state_machine.is_order_empty():
                    self.current_order = task
                    self.logs.info(f"[order] order empty,creating order ....")
                    self.execute_order(True)
                    return
                # 判断机器人当前的订单Id和新的订单Id是否一致
                if self.order_state_machine.order.orderId != task.orderId:
                    # 订单不一致，开始创建新订单逻辑
                    if not self.order_state_machine.is_order_empty():
                        self.report_error("newOrderIdButOrderRunning",
                                          state.ErrorLevel.FATAL,
                                          "orderId",
                                          str(task.orderId),
                                          err.ErrorOrder.newOrderIdButOrderRunning)
                    else:
                        # 创建新的订单
                        self.logs.info(f"[order] try to create order when order_state_machine has a order but OK！")
                        self.current_order = task
                        self.execute_order()
                    return
                # 订单一致，开始订单更新逻辑
                # orderUpdateId 比较
                elif self.order_state_machine.order.orderUpdateId <= task.orderUpdateId:
                    if self.order_state_machine.order.orderUpdateId == task.orderUpdateId:
                        self.logs.info(f"orderUpdateId已存在，丢弃信息")
                        self.report_error("orderUpdateIdExistErr",
                                          state.ErrorLevel.FATAL,
                                          "orderId",
                                          str(task.orderId),
                                          err.ErrorOrder.orderUpdateIdExistErr)
                        return
                    if self.order_state_machine.is_order_empty():
                        """ 没有任务，追加 order"""
                        self.current_order = task
                        self.execute_order(True)
                    else:
                        self.logs.info(f"[order]_try_update_order")
                        if self.is_match_node_start_end(task.nodes, self.current_order.nodes):
                            self.current_order = task
                            self.execute_order()
                            return
                        self.report_error("createOrderFailed",
                                          state.ErrorLevel.FATAL,
                                          "orderId",
                                          str(task.orderId),
                                          err.ErrorOrder.createOrderFailed)
                    return
                # orderUpdateId 比当前小，上报错误，拒绝订单
                else:
                    self.report_error("orderUpdateIdLowerErr",
                                      state.ErrorLevel.FATAL,
                                      "orderUpdateId",
                                      str(task.orderUpdateId),
                                      err.ErrorOrder.orderUpdateIdLowerErr)
            except Exception as e:
                self.logs.error(f"create order failed:{e}")
                self.report_error("createOrderFailed",
                                  state.ErrorLevel.FATAL,
                                  "orderId",
                                  str(task.orderId),
                                  err.ErrorOrder.createOrderFailed)

    def _try_update_order(self, sub_order):
        """
        用于更新订单，收到更新订单的任务，将新order和旧order拼接比较
        :param sub_order:
        :return:
        """
        self.logs.info(f"[order]_try_update_order")
        if self.is_match_node_start_end(sub_order.nodes, self.current_order.nodes):
            self.execute_order(sub_order)
            return
        self.report_error("nodeBaseErr",
                          state.ErrorLevel.WARNING,
                          "orderId",
                          str(self.current_order.orderId),
                          err.ErrorOrder.nodeBaseErr)

    def pack_send(self, new_order: order.Order):
        task_list, uuid_task = self.pack_task.pack(new_order, self.robot)
        self.logs.info(f"[pack]res:{task_list}，{uuid_task}")
        if task_list:
            self.robot.send_order(task_list)
        return uuid_task

    def is_match_node_start_end(self, new_node: List[order.Node], old_node: List[order.Node]) -> bool:
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
        if not (isinstance(new_node, list) or isinstance(old_node, list)) or len(new_node) == 0 or len(old_node) == 0:
            self.logs.error(f"new_node:{type(new_node)},{new_node}\n")
            self.logs.error(f"old_node:{type(old_node)},{old_node}\n")
            self.logs.error("校对 new base 和 old base 的 node 是否一致时，输入节点类型不是节点,或者 list 为空")
            return False
        end = None
        start = new_node[0]
        if not start.released:
            self.logs.error(f"输入的第一个节点的 base 为 {start.released}")
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

    def execute_order(self, is_new_order: bool = False):
        try:
            uuid_task = self.pack_send(self.current_order)
            self.logs.info(f"打包任务，并下发任务，下发任务的ID列表：{uuid_task}")
            self.order_state_machine.add_order(self.current_order, uuid_task, self.robot.model.agvClass)
        except Exception as e:
            self.logs.info(f"试图打包任务，发给机器人 失败:{e}")
            self.report_error("sendOrderToRobotErr",
                              state.ErrorLevel.WARNING,
                              "orderId",
                              str(self.current_order.orderId),
                              err.ErrorOrder.sendOrderToRobotErr)

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

    def _handle_actions(self):
        # 定义每种动作类型对应的处理函数
        return {
            "startPause": lambda a: self.instant_start_pause(a),
            "stopPause": lambda a: self.instant_stop_pause(a),
            "startCharging": lambda a: ActionPack.startCharging,
            "stopCharging": lambda a: ActionPack.stopCharging,
            "initPosition": lambda a: self.instant_initPosition(a),
            "stateRequest": lambda a: ActionPack.stateRequest,
            "logReport": lambda a: ActionPack.logReport,
            "Script": lambda a: self.instant_script(a),
            "cancelOrder": lambda a: self.instant_cancel_task(a),
            "factsheetRequest": lambda a: self.instant_factsheet_request(a),

        }

import json
import uuid
from src.serve.templates.html import HTML
from src.serve.robot import Robot
from src.serve.handleTopic import HandleTopic
from src.type.VDA5050 import order, instantActions
from flask import Flask, jsonify, abort, render_template_string, request
from src.type.VDA5050 import order
from src.log.log import MyLogger
from src.serve.topicQueue import TopicQueue


def response_handler(func):
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return {"code": 200, "msg": "OK" if not res else res}
        except Exception as e:
            abort(404, str(e))

    return wrapper


class HttpServer:
    def __init__(self, web_host, web_port, robot_order: HandleTopic, robot: Robot):
        self.robot = robot
        self.robot_order = robot_order
        self.log = MyLogger()
        self.app = Flask(__name__)
        self.web_host = web_host
        self.web_port = web_port
        # 添加路由
        self._add_routes()

    def _add_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string(HTML)

        @self.app.route('/get_data', methods=['GET'])
        def get_data():
            return self._get_data()

        @self.app.route('/getOrderStatus', methods=['GET'])
        def getOrderStatus():
            return self._get_order_status()

        @self.app.route('/getState', methods=['GET'])
        def getState():
            return self._get_state()

        @self.app.route('/getPackTask', methods=['GET'])
        def getPackTask():
            return self._get_pack_task()

        @self.app.route('/getPushData', methods=['GET'])
        def getPushData():
            return self._get_push_data()

        @self.app.route('/cancelOrder', methods=['POST'])
        def cancelOrder():
            return self._cancelOrder()

        @self.app.route('/startPause', methods=['POST'])
        def startPause():
            return self._start_pause()

        @self.app.route('/stopPause', methods=['POST'])
        def stopPause():
            return self._stop_pause()

        @self.app.route('/mqttMsg', methods=['POST'])
        def mqttMsg():
            return self._mqttMsg(request.data)

    def _get_data(self):
        order1 = None
        if self.robot_order.current_order:
            order1 = self.robot_order.current_order.model_dump()
        # 这里需要根据具体情况编写逻辑，在此给出一个示例
        data = {
            'current_order': order1,
            'current_order_state': self.robot.state.model_dump()
        }
        return jsonify(data)

    def _get_order_status(self):
        nodes_s, edges_s, actions_s, instantActions_s = self.robot_order.order_state_machine.get_order_status()
        nodes = {i_n: n.model_dump() for i_n, n in nodes_s.items()}
        edges = {i_e: e.model_dump() for i_e, e in edges_s.items()}
        actions = {i_a: a.model_dump() for i_a, a in actions_s.items()}
        instantAction = {i_i: i.model_dump() for i_i, i in instantActions_s.items()}

        return jsonify({
            "nodes_s": nodes,
            "edges_s": edges,
            "actions_s": actions,
            "instantActions_s": instantAction,
            "uuid_task": self.robot_order.order_state_machine.uuid_task
        })

    def _get_state(self):
        state = self.robot_order.robot.state.model_dump()
        return jsonify(state)

    def _get_pack_task(self):
        pack_task = {
            "task_pack_list": self.robot_order.pack_task.task_pack_list,
        }
        return jsonify(pack_task)

    def _get_push_data(self):
        push_data = {
            "map": {"advanced_point_list": self.robot.map.advanced_point_list,
                    "current_map": self.robot.map.current_map,
                    "current_map_md5": self.robot.map.current_map_md5},
            "PushData": self.robot_order.robot.robot_push_msg.model_dump(),
            "model_msg": self.robot.model.model_msg,
            "online_status": self.robot.rbk.online_status
        }
        return jsonify(push_data)

    def run(self):
        self.app.run(host=self.web_host, port=self.web_port)

    def create_action(self, action_type):
        return order.Action(**{
            "actionType": action_type,
            "actionId": str(uuid.uuid1()),
            "actionDescription": "http reset",
            "blockingType": "HARD",
            "actionParameters": []
        })

    @response_handler
    def _cancelOrder(self):
        self.robot_order.instant_cancel_task(self.create_action("cancelOrder"))

    @response_handler
    def _stop_pause(self):
        self.robot_order.instant_stop_pause(self.create_action("stopPause"))

    @response_handler
    def _start_pause(self):
        self.robot_order.instant_start_pause(self.create_action("startPause"))

    @response_handler
    def _mqttMsg(self, body):
        try:
            if message := json.loads(body.decode("utf-8")).get("message"):
                if isinstance(message, str):
                    message = json.loads(message)
                if isinstance(message, bytes):
                    message = json.loads(message)
                if isinstance(message, dict):
                    print(message)
                    if message.get("actions"):
                        self.robot_order.http_handle_instantActions(instantActions.InstantActions(**message))
                        print("http InstantActions")
                    elif message.get("nodes"):
                        self.robot_order.http_run_order(order.Order(**message))
                        print("http InstantActions")
                    elif message.get("id"):
                        if o := self.robot_order.sim_order.creat_order(self.robot,message):
                            self.robot_order.http_run_order(o)
                            return o.model_dump()
            self.log.info(f"[httpServer]create order")
        except Exception as e:
            self.log.error(f"[httpServer]create order error,body:{body}")
            self.log.error(f"[httpServer]create order error,msg:{e}")

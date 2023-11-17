import json
import uuid
from werkzeug.exceptions import HTTPException
from serve.templates.html import HTML
from serve.robot import Robot
from serve.handleTopic import HandleTopic
from flask import Flask, jsonify, render_template, abort,render_template_string
from type.VDA5050 import order
from log.log import MyLogger


def response_handler(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return {"code": 200, "msg": "OK"}
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
            current_order = self.robot_order.current_order
            current_order_state = self.robot_order.current_order_state
            return render_template_string(HTML, current_order=current_order, current_order_state=current_order_state)

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

    def _get_data(self):
        order1 = None
        if self.robot_order.current_order:
            order1 = self.robot_order.current_order.model_dump()
        # 这里需要根据具体情况编写逻辑，在此给出一个示例
        data = {
            'current_order': order1,
            'current_order_state': self.robot_order.current_order_state.model_dump()
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
            "PushData": self.robot_order.robot.robot_push_msg.model_dump()
        }
        return jsonify(push_data)

    def start_web(self):
        # 启动Flask应用
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

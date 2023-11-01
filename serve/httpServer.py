import json
from serve.robot import Robot
from serve.handleTopic import HandleTopic
from flask import Flask, jsonify, render_template

from log.log import MyLogger


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
            return render_template('index.html', current_order=current_order, current_order_state=current_order_state)

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
        nodes = {}
        edges = {}
        actions = {}
        instantAction = {}
        for i_n, n in nodes_s.items():
            nodes[i_n] = n.model_dump()
        for i_e, e in edges_s.items():
            edges[i_e] = e.model_dump()
        for i_a, a in actions_s.items():
            actions[i_a] = a.model_dump()
        for i_i, i in instantActions_s.items():
            instantAction[i_i] = i.model_dump()

        return jsonify({
            "nodes_s": nodes,
            "edges_s": edges,
            "actions_s": actions,
            "instantActions_s": instantAction
        })

    def _get_state(self):
        state = self.robot_order.robot.state.model_dump()
        return jsonify(state)

    def _get_pack_task(self):
        pack_task = {
            "task_pack_list": self.robot_order.pack_task.task_pack_list,
            "pack_nodes_edges_list": self.robot_order.pack_task.pack_nodes_edges_list(),
            "pack_mode": self.robot_order.pack_task.pack_mode,
            "nodes_point": self.robot_order.pack_task.nodes_point,
            "map_point": self.robot_order.pack_task.map_point if self.robot_order.pack_task.map_point else ""
        }
        return jsonify(pack_task)

    def _get_push_data(self):
        push_data = {
            "PushData": self.robot_order.robot.robot_push_msg.model_dump()
        }
        return jsonify(push_data)

    def start_web(self):
        # 启动Flask应用
        self.app.run(host=self.web_host, port=self.web_port)

    def _cancelOrder(self):
        self.robot_order.instant_cancel_task()
        data = {
            "code": 200,
            "msg": "OK"
        }
        return jsonify(data)

from enum import Enum
from type.order import Order
from type.state import State


class Status(str, Enum):
    WAITING = "WAITING"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"


class OrderStateMachine:
    def __init__(self):
        self.orders = {}

    def update_order_status(self, order_data: Order):
        order_id = order_data.orderId
        order = {
            "orderId": order_id,
            "status": Status.INITIALIZING,
            "nodes": {},
            "edges": {},
            "actions": {}
        }
        nodes = dict()
        edges = dict()
        actions = dict()
        for node in order_data.nodes:
            nodes[node.nodeId] = {
                "node": node,
                "status": Status.INITIALIZING
            }
        for edge in order_data.edges:
            edges[edge.edgeId] = {
                "node": edge,
                "status": Status.INITIALIZING
            }
        order["nodes"].update(nodes)
        order["edges"].update(edges)
        order["actions"].update(actions)

    def get_order_by_id(self, order_id):
        return self.orders.get(order_id)

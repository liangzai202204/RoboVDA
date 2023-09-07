import copy
from typing import List, Union

from action_type.action_type import ActionType, ActionPack
from serve.mode import PackMode
from type import order
from error_type import error_type as err


class PackTask:
    def __init__(self, pack_mode:PackMode, map_point=None):
        self.nodes_point = None
        self.map_point = map_point
        self.pack_mode = pack_mode
        self.map_point = map_point  # 保存了地图的站点
        self.order = None
        self.nodes: List[order.Node] = []
        self.edges: List[order.Edge] = []
        self.nodes_edges_list = []
        self.task_pack_list = []
        self.error = None

    def pack(self, new_order: order.Order,map_point):
        self.clear_pack()
        self.map_point = map_point
        self.order = new_order
        self.nodes = copy.deepcopy(new_order.nodes)
        self.edges = copy.deepcopy(new_order.edges)
        # 检查 order 内容 并排序 nodes 和 edges
        if not self.nodes or not self.edges:
            return err.ErrorOrder.nodeOrEdgeEmpty
        if (len(self.nodes) - 1) != len(self.edges):
            return err.ErrorOrder.nodeAndEdgeNumErr

        self.nodes.sort(key=lambda x: x.sequenceId)
        self.nodes.sort(key=lambda y: y.sequenceId)
        # 将 nodes 和 edge 打包入列表中，结构为 [edge,node,edge,node,...,edge,node]
        l_err = self.pack_nodes_edges_list()
        if isinstance(l_err, err.ErrorOrder):
            return l_err
        if self.pack_mode == PackMode.vda5050:
            self.pack_vda5050()
        elif self.pack_mode == PackMode.binTask:
            self.pack_binTask()
        elif self.pack_mode == PackMode.params:
            self.pack_params()
        if self.error:
            return self.error
        return self.task_pack_list

    def pack_nodes_edges_list(self):
        """
        将 node 和 edge 的任务打包在一起
        :param nodes:
        :param edges:
        :return:list
        """
        try:
            nodes = copy.deepcopy(self.nodes)
            edges = copy.deepcopy(self.edges)
            while nodes and edges:
                node = nodes.pop(0)
                edge = edges.pop(0)

                self.nodes_edges_list.append(node)
                self.nodes_edges_list.append(edge)

                if edge.startNodeId != node.nodeId:
                    return err.ErrorOrder.startNodeIdNotNodeId
                if str(edge.endNodeId) != str(nodes[0].nodeId):
                    return err.ErrorOrder.endNodeIdNotNodeId
                if not edges and nodes:
                    self.nodes_edges_list.append(nodes[-1])
            self.nodes_edges_list = self.nodes_edges_list[1:]
            return True
        except Exception as e:
            print(f"pack_nodes_edges_list error:{e}")

    def do_pack(self):
        if self.pack_mode != PackMode.vda5050:
            self.pack_vda5050()
        if self.pack_mode != PackMode.binTask:
            self.pack_binTask()
        if self.pack_mode != PackMode.params:
            self.pack_params()

    def pack_vda5050(self):
        pass

    def pack_binTask(self):
        self.load_map_point_in_order()
        for edge, node in zip(self.nodes_edges_list[::2], self.nodes_edges_list[1::2]):
            node: order.Node
            edge: order.Edge
            self.pack_edge(edge, node)
            self.pack_node(node)

    def pack_params(self):
        try:
            self.load_map_point_in_order()
            for edge, node in zip(self.nodes_edges_list[::2], self.nodes_edges_list[1::2]):
                node: order.Node
                edge: order.Edge
                self.pack_edge(edge, node)
                self.pack_node(node)
        except Exception as e:
            print(f"pack_params error:{e}")

    def load_map_point_in_order(self):
        try:
            self.nodes_point = {
                node.nodeId: self.map_point.get((node.nodePosition.x, node.nodePosition.y))
                for node in self.nodes
            }
        except Exception as e:
            print(f"load_map_point_in_order:{e}")
            self.error = err.ErrorOrder.orderNodeGetMapPointErr

    def pack_node(self, node:order.Node):
        if node.actions:
            self.pack_actions(node)

    def pack_edge(self, edge:order.Edge, node:order.Node):
        edge_start_point = self.nodes_point.get(edge.startNodeId)
        edge_end_point = self.nodes_point.get(edge.endNodeId)
        if not edge_start_point or not edge_end_point:
            self.error = err.ErrorOrder.mapNotNodePosition
            return
        if edge_start_point and edge_end_point:
            edge_task = {
                "task_id": edge.edgeId,
                "id": edge_end_point,
                "source_id": edge_start_point,
                "operation": "Wait",
                "percentage": 1.0
            }

            if (not node.nodePosition.theta or node.nodePosition.theta == 0) and edge.actions is None:
                edge_task["reach_angle"] = 3.141592653589793
            edge_task["angle"] = node.nodePosition.theta

            if edge.actions:
                self.pack_actions(edge,edge_task)

            if edge.released:
                self.task_pack_list.append(edge_task)
        else:
            print("地图没点",edge.startNodeId,edge.edgeId)
            self.error = err.ErrorPckTask.mapNotNodePosition

    def pack_actions(self, NE: Union[order.Node, order.Edge],edge_task=None):
        actions = NE.actions
        for action in actions:
            action_task = ActionPack.pack(action, self.pack_mode)
            if not action_task:
                print("action_task error:", action_task)
                self.error = err.ErrorOrder.actionPackEmpty
                return
            if isinstance(NE,order.Node):
                if NE.released:
                    self.task_pack_list.append(action_task)
            if isinstance(NE,order.Edge):
                if edge_task:
                    edge_task["script_name"] = action_task["script_name"]
                    edge_task["script_args"] = action_task["script_args"]
                    edge_task["operation"] = action_task["operation"]
                    edge_task["script_stage"] = 1


    def clear_pack(self):
        self.nodes = []
        self.edges = []
        self.nodes_edges_list = []
        self.task_pack_list = []



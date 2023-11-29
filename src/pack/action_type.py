from typing import Union
from src.type.VDA5050 import order
import pydantic
from src.serve.robot import Robot as Robot
from src.config.config import Config

instant_action_type = ['startPause', 'stopPause', 'startCharging',
                       'stopCharging', 'initPosition', 'stateRequest',
                       'logReport', 'factsheetRequest', 'cancelOrder']


class ActionType:
    PICK = "pick"
    PICK_FORK = "pick"
    DROP_FORK = "drop"
    DROP = "drop"
    FORK_LIFT = "forklift"
    FORK_LOAD = "ForkLoad"
    FORK_UNLOAD = "ForkUnload"
    TEST = "test"
    Angle = "angle"
    Ready = "ready"
    Script = "Script"
    FactsheetRequest = "factsheetRequest"
    SafeCheck = "safeCheck"


class ActionPack(pydantic.BaseModel):

    """
    script_stage = 1

    """

    @classmethod
    def pack_action_script(cls, action: order.Action, action_uuid, config: Config = None):
        action_task = {}
        operation = None
        script_name = None
        for ap in action.actionParameters:
            if ap.key == "operation":
                operation = ap.value
            if ap.key == "script_name":
                script_name = ap.value
        action_task["operation"] = operation if operation else ActionType.Script
        action_task["script_name"] = script_name if script_name else config.script_name
        action_task["script_args"] = {"action_parameters": [a.model_dump() for a in action.actionParameters],
                                      "operation": action.actionType}
        action_task["id"] = "SELF_POSITION"
        action_task["source_id"] = "SELF_POSITION"
        action_task["task_id"] = action_uuid
        return action_task

    @classmethod
    def pack_action_fork(cls, action: order.Action, action_uuid, config):
        action_task = {}
        operation = None
        for ap in action.actionParameters:
            if ap.key == "operation":
                operation = ap.value
            elif ap.key == "script_name":
                action_task["script_name"] = ap.value
            elif ap.key == "recfile":
                action_task["recfile"] = ap.value
            elif ap.key == "start_height":
                action_task["start_height"] = ap.value

            elif ap.key == "rec_height":
                action_task["rec_height"] = ap.value

            elif ap.key == "end_height":
                action_task["end_height"] = ap.value

            elif ap.key == "recognize":
                action_task["recognize"] = ap.value
        if operation == ActionType.Script or action.actionType == ActionType.Script:
            return ActionPack.pack_action_script(action, action_uuid)
        if not operation:
            if action.actionType == ActionType.PICK:
                operation = "ForkLoad"
            elif action.actionType == ActionType.DROP:
                operation = "ForkUnload"
            else:
                print(f"[ActionPack] action.actionType or operation error:{action.actionType}")
                return {}
        action_task["operation"] = operation
        action_task["id"] = "SELF_POSITION"
        action_task["source_id"] = "SELF_POSITION"
        action_task["task_id"] = action_uuid
        return action_task

    @classmethod
    def pack_action_jack(cls, action: order.Action, action_uuid, config):
        action_task = {}
        operation = None
        for ap in action.actionParameters:
            if ap.key == "operation":
                operation = ap.value
            elif ap.key == "script_name":
                action_task["script_name"] = ap.value
            elif ap.key == "recfile":
                action_task["recfile"] = ap.value
            elif ap.key == "jack_height":
                action_task["jack_height"] = float(ap.value)

            elif ap.key == "use_down_pgv":
                action_task["use_down_pgv"] = bool(ap.value)

            elif ap.key == "use_pgv":
                action_task["use_pgv"] = bool(ap.value)

            elif ap.key == "recGoOut":
                action_task["recGoOut"] = bool(ap.value)
            elif ap.key == "recognize":
                action_task["recognize"] = bool(ap.value)
        if operation == ActionType.Script or action.actionType == ActionType.Script:
            return ActionPack.pack_action_script(action,action_uuid)
        if not operation:
            if action.actionType == ActionType.PICK:
                operation = "JackLoad"
            elif action.actionType == ActionType.DROP:
                operation = "JackUnload"
            else:
                print(f"[ActionPack] action.actionType or operation error:{action.actionType}")
                return {}
        action_task["operation"] = operation
        action_task["id"] = "SELF_POSITION"
        action_task["source_id"] = "SELF_POSITION"
        action_task["task_id"] = action_uuid
        return action_task

    @classmethod
    def pack_action(cls, action: order.Action, action_uuid, robot: Robot, config: Config):
        try:
            if not action_uuid:
                action_uuid = action.actionId
            action_task = {}
            if robot.model.agvClass == "FORKLIFT":
                return ActionPack.pack_action_fork(action, action_uuid, config)
            elif robot.model.agvClass == "CARRIER":
                return ActionPack.pack_action_jack(action, action_uuid, config)
            elif robot.model.agvClass == "NONE":
                return ActionPack.pack_action_script(action, action_uuid, config)
            else:
                print(f"[ActionPack]不支持类型:{robot.model.agvClass}")
            print(f"[pack][{action.actionType}]:{action_task}")
            return action_task
            # action_mapping = {
            #     ActionType.PICK: lambda a: ActionPack.pick(a,script_name),
            #     ActionType.DROP: lambda a: ActionPack.drop(a, script_name),
            #     ActionType.FORK_LIFT: lambda a: ActionPack.forklift(a, script_name),
            #     ActionType.TEST: lambda a: ActionPack.test(a, script_name),
            #     ActionType.FORK_LOAD: lambda a: ActionPack.fork_load(a, script_name),
            #     ActionType.FORK_UNLOAD: lambda a: ActionPack.fork_unload(a, script_name),
            #     ActionType.Angle: lambda a: ActionPack.angle_action(a, script_name),
            #     ActionType.Ready: lambda a: ActionPack.ready(a, script_name),
            #     # ActionType.PICK_FORK: lambda a: ActionPack.pick_fork(a, script_stage=1),
            #     # ActionType.DROP_FORK: lambda a: ActionPack.drop_fork(a, script_stage=1),
            # }
            #
            # action_type = action.actionType
            # if action_type in action_mapping:
            #     print(action_type)
            #     action_task = action_mapping[action_type](action)
            # else:
            #     print("不支持动作类型：", action_type, action.actionParameters)
        except Exception as e:
            print(f"action pack error:{e}")

    @classmethod
    def pack_edge(cls, edge: order.Edge, start_node: Union[order.NodePosition, order.Node],
                  end_node: Union[order.NodePosition, order.Node], uuid_task: str, robot: Robot, config: Config):
        action_task = {}
        if edge.trajectory:
            if isinstance(start_node, order.Node) and isinstance(end_node, order.Node):
                for endNode_a in end_node.actions:
                    if endNode_a.actionType == ActionType.PICK or endNode_a.actionType == ActionType.DROP:
                        if robot.model.agvClass == "FORKLIFT" or robot.model.agvClass == "CARRIER":
                            action_task = ActionPack.pack_action(endNode_a, uuid_task, robot, config)
                            action_task["sourcePos"] = start_node.nodePosition.model_dump()
                            action_task["targetPos"] = end_node.nodePosition.model_dump()
                            action_task["trajectory"] = edge.trajectory.model_dump()
                            action_task["id"] = edge.endNodeId
                            action_task["source_id"] = edge.startNodeId
                            action_task["task_id"] = uuid_task
                    else:
                        print(f"[actionPack] ActionType:{endNode_a.actionType}")
                        return {}
            elif isinstance(start_node, order.NodePosition) and isinstance(end_node, order.NodePosition):
                if len(edge.actions) == 1:
                    for e_a in edge.actions:
                        if e_a.blockingType == order.ActionBlockingType.HARD:
                            action_task["script_stage"] = 2
                        elif e_a.blockingType == order.ActionBlockingType.NONE:
                            action_task["script_stage"] = 1
                        elif e_a.blockingType == order.ActionBlockingType.SOFT:
                            action_task["script_stage"] = 1
                        action_task["operation"] = "Script"
                        script_name = None
                        for ap in e_a.actionParameters:
                            if ap.key == "script_name":
                                script_name = ap.value
                        action_task["script_name"] = script_name if script_name else config.script_name
                        action_task["script_args"] = {
                            "action_parameters": [a.model_dump() for a in e_a.actionParameters],
                            "operation": e_a.actionType
                        }
                action_task["sourcePos"] = start_node.model_dump()
                action_task["targetPos"] = end_node.model_dump()
                action_task["trajectory"] = edge.trajectory.model_dump()
                if edge.holdDir is not None:
                    action_task["hold_dir"] = edge.holdDir
                action_task["id"] = edge.endNodeId
                action_task["source_id"] = edge.startNodeId
                action_task["task_id"] = uuid_task
            else:
                print(f"[actionPack] start_node or end_node type error:{start_node},{end_node}")
                return {}
        else:
            if isinstance(start_node, order.Node) and isinstance(end_node, order.Node):
                for endNode_a in end_node.actions:
                    if endNode_a.actionType == ActionType.PICK or endNode_a.actionType == ActionType.DROP:
                        if robot.model.agvClass == "FORKLIFT" or robot.model.agvClass == "CARRIER":
                            action_task = ActionPack.pack_action(endNode_a, uuid_task, robot, config)
                            start_id = robot.map.XYDir.get(
                                (start_node.nodePosition.x, start_node.nodePosition.y, start_node.nodePosition.theta))
                            end_id = robot.map.XYDir.get(
                                (end_node.nodePosition.x, end_node.nodePosition.y, end_node.nodePosition.theta))
                            if not start_id and not end_id:
                                print("map no point3", start_id, end_id)
                                return {}
                            action_task["id"] = end_id
                            action_task["source_id"] = start_id
                            action_task["task_id"] = uuid_task
                    else:
                        print(f"[actionPack] ActionType:{endNode_a.actionType}")
                        return {}
            elif isinstance(start_node, order.NodePosition) and isinstance(end_node, order.NodePosition):
                if len(edge.actions) == 1:
                    for e_a in edge.actions:
                        if e_a.blockingType == order.ActionBlockingType.HARD:
                            action_task["script_stage"] = 2
                        elif e_a.blockingType == order.ActionBlockingType.NONE:
                            action_task["script_stage"] = 1
                        elif e_a.blockingType == order.ActionBlockingType.SOFT:
                            action_task["script_stage"] = 1
                        action_task["operation"] = "Script"
                        script_name = None
                        for ap in e_a.actionParameters:
                            if ap.key == "script_name":
                                script_name = ap.value
                        action_task["script_name"] = script_name if script_name else config.script_name
                        action_task["script_args"] = {
                            "action_parameters": [a.model_dump() for a in e_a.actionParameters],
                            "operation": e_a.actionType}
                if edge.holdDir:
                    action_task["hold_dir"] = edge.holdDir
                start_id = robot.map.XYDir.get(
                    (start_node.x, start_node.y, start_node.theta))
                end_id = robot.map.XYDir.get(
                    (end_node.x, end_node.y, end_node.theta))
                print("task point", start_id, end_id)
                if not start_id and not end_id:
                    print("map no point", start_id, end_id)
                    return {}
                action_task["id"] = end_id
                action_task["source_id"] = start_id
                action_task["task_id"] = uuid_task
            else:
                print(f"[actionPack] start_node or end_node type error:{start_node},{end_node}")
                return {}
            return action_task

        return action_task

    @staticmethod
    def startPause(action: order.Action) -> dict:
        a = dict()
        print(action)
        return a

    @staticmethod
    def stopPause(action: order.Action) -> dict:
        a = dict()
        print(action)
        return a

    @staticmethod
    def startCharging(action: order.Action) -> dict:
        a = dict()
        print(action)
        return a

    @staticmethod
    def stopCharging(action: order.Action) -> dict:
        a = dict()
        print(action)
        return a

    @staticmethod
    def initPosition(action: order.Action) -> dict:
        if not action.actionParameters:
            return {}
        freeGo = {}
        for a_p in action.actionParameters:
            if a_p.key == "x":
                freeGo["x"] = a_p.value
            elif a_p.key == "y":
                freeGo["y"] = a_p.value
            elif a_p.key == "theta":
                freeGo["theta"] = a_p.value
        if not (freeGo.get("x") and freeGo.get("y") and freeGo.get("theta")):
            return {}
        args = {
            "x": freeGo.get("x"),
            "y": freeGo.get("y"),
            "theta": freeGo.get("theta"),
            "reachAngle": 0.05,
            "reachDist": 0.05,
            "coordinate": "world",
            "maxSpeed": 1,
            "maxRot": 1
        }
        task = {
            "task_id": action.actionId,
            "id": "SELF_POSITION",
            "operation": "Script",
            "script_args": args,
            "script_name": "syspy/goPath.py",
            "source_id": "SELF_POSITION"
        }
        return task

    @staticmethod
    def stateRequest(action: order.Action) -> dict:
        a = dict()
        print(action)

        return a

    @staticmethod
    def logReport(action: order.Action) -> dict:
        a = dict()
        print(action)

        return a

    @classmethod
    def pick(cls, action: order.Action, script_name) -> dict:
        action_task = cls._pack_action(action, script_name)
        print("pick:", action_task)
        return action_task

    @classmethod
    def drop(cls, action: order.Action, script_name) -> dict:
        action_task = cls._pack_action(action, script_name)
        print("drop:", action_task)
        return action_task

    @classmethod
    def drop_fork(cls, action: order.Action, script_name) -> dict:
        action_task = cls._pack_fork_action(action, script_name)
        print("drop_fork:", action_task)
        return action_task

    @classmethod
    def pick_fork(cls, action: order.Action, script_name) -> dict:
        action_task = cls._pack_fork_action(action, script_name)
        print("pick_fork:", action_task)
        return action_task

    @classmethod
    def forklift(cls, action: order.Action, script_name) -> dict:
        action_task = cls._pack_action(action, script_name)
        print("forklift:", action_task)
        return action_task

    @classmethod
    def test(cls, action: order.Action, script_name) -> dict:
        action_task = {
            "task_id": action.actionId,
            "id": "SELF_POSITION",
            "source_id": "SELF_POSITION",
            "operation": "Wait",
            "script_stage": script_name
        }
        print("test:", action_task)
        return action_task

    @classmethod
    def fork_load(cls, action: order.Action, script_name) -> dict:
        action_task = {
            "task_id": action.actionId,
            "id": "SELF_POSITION",
            "source_id": "SELF_POSITION",
            "operation": action.actionType,
            "script_stage": script_name
        }
        print("fork_load:", action_task)
        return action_task

    @classmethod
    def fork_unload(cls, action: order.Action, script_name) -> dict:
        action_task = {
            "task_id": action.actionId,
            "id": "SELF_POSITION",
            "source_id": "SELF_POSITION",
            "operation": action.actionType,
            "script_stage": script_name
        }
        print("fork_load:", action_task)

        return action_task

    @classmethod
    def angle_action(cls, action: order.Action, script_name) -> dict:
        action_task = cls._pack_action(action, script_name)
        print("angle:", action_task)
        return action_task

    @classmethod
    def ready(cls, action: order.Action, script_name) -> dict:
        action_task = cls._pack_action(action, script_name)
        print("ready:", action_task)
        return action_task

    @classmethod
    def _pack_action(cls, action: order.Action, script_name) -> dict:
        try:
            action_task = {
                "task_id": action.actionId,
                "id": "SELF_POSITION",
                "source_id": "SELF_POSITION",
                "script_name": script_name,
                "script_args": {
                    "action_parameters": [a.model_dump() for a in action.actionParameters],
                    "operation": action.actionType,
                },
                "operation": "Script",
            }
            return action_task
        except Exception as e:
            print("_pack_action error:", e)
            return {}

    @classmethod
    def _pack_fork_action(cls, action: order.Action, script_name) -> dict:
        end_height = 0
        try:
            for a_p in action.actionParameters:
                if a_p.key == "height":
                    end_height = a_p.value
            action_task = {
                "task_id": action.actionId,
                "id": "SELF_POSITION",
                "source_id": "SELF_POSITION",
                "operation": "ForkLoad" if action.actionType == ActionType.PICK_FORK else "ForkUnload",
                "end_height": end_height
            }
            return action_task
        except Exception as e:
            print("_pack_action error:", e)
            return {}

    @staticmethod
    def detectObject(action: order.Action) -> dict:
        a = dict()
        print(action)

        return a

    @staticmethod
    def finePositioning(action: order.Action) -> dict:
        a = dict()
        print(action)

        return a

    @staticmethod
    def waitForTrigger(action: order.Action) -> dict:
        a = dict()
        print(action)

        return a

    @staticmethod
    def cancelOrder(action: order.Action) -> dict:
        a = dict()
        print(action)

        return a

    @staticmethod
    def factsheetRequest(action: order.Action) -> dict:
        a = dict()
        print(action)

        return a

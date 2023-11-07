from type.VDA5050 import order
import pydantic
from type.mode import PackMode
from type.moveTaskList import Task

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


class ActionPack(pydantic.BaseModel):
    """
    script_stage = 1

    """

    @classmethod
    def pack(cls, action: order.Action):
        try:
            action_task = {}
            action_mapping = {
                ActionType.PICK: lambda a: ActionPack.pick(a),
                ActionType.DROP: lambda a: ActionPack.drop(a, script_stage=1),
                ActionType.FORK_LIFT: lambda a: ActionPack.forklift(a, script_stage=1),
                ActionType.TEST: lambda a: ActionPack.test(a, script_stage=1),
                ActionType.FORK_LOAD: lambda a: ActionPack.fork_load(a, script_stage=1),
                ActionType.FORK_UNLOAD: lambda a: ActionPack.fork_unload(a, script_stage=1),
                ActionType.Angle: lambda a: ActionPack.angle_action(a, script_stage=1),
                ActionType.Ready: lambda a: ActionPack.ready(a, script_stage=1),
                # ActionType.PICK_FORK: lambda a: ActionPack.pick_fork(a, script_stage=1),
                # ActionType.DROP_FORK: lambda a: ActionPack.drop_fork(a, script_stage=1),
            }

            action_type = action.actionType
            if action_type in action_mapping:
                print(action_type)
                action_task = action_mapping[action_type](action)
            else:
                print("不支持动作类型：", action_type, action.actionParameters)
            return action_task
        except Exception as e:
            print(f"action pack error:{e}")

    @classmethod
    def pack_edge(cls, edge: order.Edge, start_node: order.NodePosition, end_node: order.NodePosition, ):
        action_task = {}
        if edge.trajectory:
            action_task["trajectory"] = edge.trajectory.model_dump()
            if len(edge.actions) == 1:
                for e_a in edge.actions:
                    if e_a.blockingType == order.ActionBlockingType.HARD:
                        action_task["script_stage"] = 2
                    elif e_a.blockingType == order.ActionBlockingType.NONE:
                        action_task["script_stage"] = 1
                    elif e_a.blockingType == order.ActionBlockingType.SOFT:
                        action_task["script_stage"] = 1
                    action_task["operation"] = "Script"
                    action_task["script_name"] = "ForkByModbusTcpCtr.py"
                    action_task["script_args"] = [a.model_dump() for a in e_a.actionParameters]
            action_task["id"] = edge.endNodeId
            action_task["source_id"] = edge.startNodeId
            action_task["task_id"] = edge.edgeId
            action_task["sourcePos"] = start_node.model_dump()
            action_task["targetPos"] = end_node.model_dump()

        else:
            print(f"edge not has trajectory")
            print(f"edge's action only support one action")
            return {}

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
    def pick(cls, action: order.Action, script_stage=2) -> dict:
        action_task = cls._pack_action(action, script_stage)
        print("pick:", action_task)
        return action_task

    @classmethod
    def drop(cls, action: order.Action, script_stage=2) -> dict:
        action_task = cls._pack_action(action, script_stage)
        print("drop:", action_task)
        return action_task

    @classmethod
    def drop_fork(cls, action: order.Action, script_stage=2) -> dict:
        action_task = cls._pack_fork_action(action, script_stage)
        action_task.pop("script_stage")
        print("drop_fork:", action_task)
        return action_task

    @classmethod
    def pick_fork(cls, action: order.Action, script_stage=2) -> dict:
        action_task = cls._pack_fork_action(action, script_stage)
        action_task.pop("script_stage")
        print("pick_fork:", action_task)
        return action_task

    @classmethod
    def forklift(cls, action: order.Action, script_stage=2) -> dict:
        action_task = cls._pack_action(action, script_stage)
        print("forklift:", action_task)
        return action_task

    @classmethod
    def test(cls, action: order.Action, script_stage=2) -> dict:
        action_task = {
            "task_id": action.actionId,
            "id": "SELF_POSITION",
            "source_id": "SELF_POSITION",
            "operation": "Wait",
            "script_stage": script_stage
        }
        print("test:", action_task)
        return action_task

    @classmethod
    def fork_load(cls, action: order.Action, script_stage=2) -> dict:
        action_task = {
            "task_id": action.actionId,
            "id": "SELF_POSITION",
            "source_id": "SELF_POSITION",
            "operation": action.actionType,
            "script_stage": script_stage
        }
        print("fork_load:", action_task)
        return action_task

    @classmethod
    def fork_unload(cls, action: order.Action, script_stage=2) -> dict:
        action_task = {
            "task_id": action.actionId,
            "id": "SELF_POSITION",
            "source_id": "SELF_POSITION",
            "operation": action.actionType,
            "script_stage": script_stage
        }
        print("fork_load:", action_task)

        return action_task

    @classmethod
    def angle_action(cls, action: order.Action, script_stage=2) -> dict:
        action_task = cls._pack_action(action, script_stage)
        action_task.pop("script_stage")
        print("angle:", action_task)
        return action_task

    @classmethod
    def ready(cls, action: order.Action, script_stage=2) -> dict:
        action_task = cls._pack_action(action, script_stage)
        print("ready:", action_task)
        return action_task

    @classmethod
    def _pack_action(cls, action: order.Action, script_stage) -> dict:
        try:
            action_task = {
                "task_id": action.actionId,
                "id": "SELF_POSITION",
                "source_id": "SELF_POSITION",
                "script_name": "ForkByModbusTcpCtr.py",
                "script_args": {
                    "action_parameters": [a.model_dump() for a in action.actionParameters],
                    "operation": action.actionType,
                    "blocking_type": "node"
                },
                "operation": "Script",
                "script_stage": script_stage
            }
            return action_task
        except Exception as e:
            print("_pack_action error:", e)
            return {}

    @classmethod
    def _pack_fork_action(cls, action: order.Action, script_stage) -> dict:
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

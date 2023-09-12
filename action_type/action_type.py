from type import order
import pydantic
from serve.mode import PackMode


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
    def pack(cls, action: order.Action, pack_mode):
        action_task = None
        if action.actionType == ActionType.PICK:
            action_task = ActionPack.pick(action, pack_mode)
        elif action.actionType == ActionType.DROP:
            action_task = ActionPack.drop(action, pack_mode)
        elif action.actionType == ActionType.FORK_LIFT:
            action_task = ActionPack.forklift(action, pack_mode, script_stage=1)
        elif action.actionType == ActionType.TEST:
            action_task = ActionPack.test(action, pack_mode)
        elif action.actionType == ActionType.FORK_LOAD:
            action_task = ActionPack.fork_load(action, pack_mode)
        elif action.actionType == ActionType.FORK_UNLOAD:
            action_task = ActionPack.fork_unload(action, pack_mode)
        elif action.actionType == ActionType.Angle:
            action_task = ActionPack.angle_action(action, pack_mode)
        elif action.actionType == ActionType.Ready:
            action_task = ActionPack.ready(action, pack_mode)
        elif action.actionType == ActionType.PICK_FORK:
            action_task = ActionPack.pick_fork(action, pack_mode)
        elif action.actionType == ActionType.DROP_FORK:
            action_task = ActionPack.drop_fork(action, pack_mode)
        else:
            print("不支持动作类型：", action.actionType, action.actionParameters)
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
        task = {
            "task_id": action.actionId,
            "id": "SELF_POSITION",
            "freeGo": freeGo
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
    def pick(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
        action_task = cls._pack_action(action, mode, script_stage)
        print("pick:", action_task)
        return action_task

    @classmethod
    def drop(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
        action_task = cls._pack_action(action, mode, script_stage)
        print("drop:", action_task)
        return action_task

    @classmethod
    def drop_fork(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
        action_task = cls._pack_fork_action(action, mode, script_stage)
        print("drop_fork:", action_task)
        return action_task

    @classmethod
    def pick_fork(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
        action_task = cls._pack_fork_action(action, mode, script_stage)
        print("pick_fork:", action_task)
        return action_task

    @classmethod
    def forklift(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
        action_task = cls._pack_action(action, mode, script_stage)
        print("forklift:", action_task)
        return action_task

    @classmethod
    def test(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
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
    def fork_load(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
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
    def fork_unload(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
        action_task = {
            "task_id": action.actionId,
            "id": "SELF_POSITION",
            "source_id": "SELF_POSITION",
            "operation": action.actionType,
            "script_stage": script_stage
        }
        print("fork_load:", action_task)
        return action_task

    def angle_action(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
        action_task = cls._pack_action(action, mode, script_stage)
        print("angle:", action_task)
        return action_task

    def ready(cls, action: order.Action, mode: PackMode, script_stage=2) -> dict:
        action_task = cls._pack_action(action, mode, script_stage)
        print("ready:", action_task)
        return action_task

    @classmethod
    def _pack_action(cls, action: order.Action, mode: PackMode, script_stage) -> dict:
        try:
            if not (mode != PackMode.params or mode != PackMode.binTask):
                print("action type error:", mode)
                return {}
            if mode == PackMode.params:
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
            elif mode == PackMode.binTask:
                action_task = {
                    "task_id": action.actionId
                }
                for param in action.actionParameters:
                    if param.key == "binTask":
                        action_task["binTask"] = param.value
                    if param.key == "id":
                        action_task["id"] = param.value
                        action_task["source_id"] = param.value
                if not (action_task.get("id") and action_task.get("binTask")):
                    print(f"动作打包异常(binTask模式)！！！ action_task：{action_task}|||action：{action}")
                    return {}
                return action_task
        except Exception as e:
            print("_pack_action error:", e)
            return {}
    @classmethod
    def _pack_fork_action(cls, action: order.Action, mode: PackMode, script_stage) -> dict:
        end_height = 0
        try:
            if not (mode != PackMode.params or mode != PackMode.binTask):
                print("action type error:", mode)
                return {}
            for a_p in action.actionParameters:
                if a_p.key == "height":
                    end_height = a_p.value
            if mode == PackMode.params:
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

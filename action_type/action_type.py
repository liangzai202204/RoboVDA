from type import order
import pydantic
from serve.mode import PackMode


class ActionType:
    PICK = "pick"
    DROP = "drop"
    FORK_LIFT = "forklift"


class ActionPack(pydantic.BaseModel):

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
        a = dict()
        print(action)

        return a

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
    def _pack_action(cls, action: order.Action, mode: PackMode, script_stage) -> dict:
        try:
            if mode == PackMode.params:
                action_task = {
                    "task_id": action.actionId,
                    "id": "SELF_POSITION",
                    "source_id": "SELF_POSITION",
                    "script_name": "ForkByModbusTcpCtr.py",
                    "script_args": {
                        "action_parameters": action.actionParameters,
                        "operation": action.actionType,
                        "blocking_type": "node"
                    },
                    "operation": "Script",
                    "script_stage": script_stage
                }
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
                    print(f"动作打包异常！！！ action_task：{action_task}|||action：{action}")
                    action_task = {}
            else:
                print("action type error:", mode)
                action_task = {}
            return action_task
        except Exception as e:
            print("_pack_action error:",e)
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

from type import order
import pydantic


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

    @staticmethod
    def pick(action: order.Action,node_id:str) -> dict:
        # print("pick")
        action_parameters = action.actionParameters
        station_name = None
        station_type = None
        try:
            for action_parameter in action_parameters:
                # print("------",action_parameter.dict())
                a_p = action_parameter.dict()
                if a_p["key"] == "stationName":
                    station_name = a_p["value"]
                if a_p["key"] == "stationType":
                    station_type = a_p["value"]
        except Exception as e:
            print("pick action failed", e)
        if station_type and station_name:
            a = {
                "id": station_name,
                "source_id":node_id,
                "task_id": action.actionId,
                "binTask": station_type
            }
            return a
        return {}

    @staticmethod
    def drop(action: order.Action) -> dict:
        # print("pick")
        action_parameters = action.actionParameters
        station_name = None
        station_type = None
        try:
            for action_parameter in action_parameters:
                # print("------",action_parameter.dict())
                a_p = action_parameter.dict()
                if a_p["key"] == "stationName":
                    station_name = a_p["value"]
                if a_p["key"] == "stationType":
                    station_type = a_p["value"]
            print("ssss", station_name, station_type)
        except Exception as e:
            print("pick action failed", e)
        if station_type and station_name:
            a = {
                "id": station_name,
                "task_id": action.actionId,
                "binTask": station_type
            }
            return a
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

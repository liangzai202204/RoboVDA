import json
import os
import time
from syspy.rbkSim import SimModule
from syspy.rbk import MoveStatus, BasicModule

"""
####BEGIN DEFAULT ARGS####
{    
    "operation": {
        "value": "",
        "default_value": [
            "restart"
        ],
        "tips": "tips",
        "type": "complex"
    }
}

####END DEFAULT ARGS####
"""


class Module(BasicModule):
    def __init__(self, r: SimModule, args):
        super().__init__()
        self.motor_name = "test"
        self.init = True
        self.state = {}
        self.init_time = time.time()

    def periodRun(self, r: SimModule):
        # self.state["task"] = r.moveTask()
        # self.state["taskSTATUS"] = r.getCurrentTaskStatus()
        # # if ModuleTool.check_DI(r,2):
        # #     r.stopRobot(True)
        r.setInfo(json.dumps(self.state))
        r.logInfo(json.dumps(self.state))
        return True

    def run(self, r: SimModule, args: dict):
        if "operation" in args:
            if args["operation"] == "restart":
                os.system(
                    f"/bin/bash /home/seer/PycharmProjects/RoboVDA3/SeerRobotics/RoboVda-SRC/usr/local/SeerRobotics/vda/restart_RoboVda.sh")
                self.status = MoveStatus.FINISHED
        else:
            self.status = MoveStatus.FAILED
        return self.status


if __name__ == '__main__':
    pass

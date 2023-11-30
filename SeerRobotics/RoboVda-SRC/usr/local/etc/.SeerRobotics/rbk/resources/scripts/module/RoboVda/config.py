import json
import os
import stat
import time
from syspy.rbkSim import SimModule
from syspy.rbk import MoveStatus, BasicModule
"""
####BEGIN DEFAULT ARGS####
{    
    "operation": {
        "value": "",
        "default_value": [
            "config"
        ],
        "tips": "tips",
        "type": "complex"
    },
    "args": {
        "value": "",
        "default_value": "",
        "tips": "tips",
        "type": "string"
    }
}

####END DEFAULT ARGS####
"""
class Module(BasicModule):
    def __init__(self, r: SimModule, args):
        super().__init__()
        self.state = {}
        self.init_time = time.time()

    def periodRun(self, r: SimModule):
        r.setInfo(json.dumps(self.state))
        r.logInfo(json.dumps(self.state))
        return True

    def run(self, r: SimModule, args: dict):
        if "operation" in args:
            if args["operation"] == "config":
                if not os.path.exists("/usr/local/SeerRobotics/vda/"):
                    os.makedirs("/usr/local/SeerRobotics/vda/")
                # 将配置内容写入文件
                path = os.path.join("/usr/local/SeerRobotics/vda/", 'config.ini')
                with open(path, 'w') as file:
                    file.write(str(args["args"]))
                os.chmod(path,stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
                # 更新状态和日志
                self.status = MoveStatus.FINISHED
        return self.status

CONFIG ="""

"""

if __name__ == '__main__':
    pass
import json
import time
import unittest
import rbklib
from serve.pushMsgType import RobotPush


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_rbklib(self):
        r = rbklib.Rbklib("192.168.8.175")
        a, b = r.robot_status_task_status_package_req(
            ['7a434ec3-91c8-4334-89f8-31d30942fbb7', '11119fc4-7fe4-4a91-b6be-210a065131da'])
        print(b)

    def test_rbklib_1400(self):
        r = rbklib.Rbklib("192.168.8.152")
        a, b = r.robot_status_params_req(param={
            "MoveFactory": ["MaxAcc"],
            "DSPChassis": ["RemoteIP"],
            "ArmAdapter": ["ArmOperationTimeout", "ArminfoPublishTime"]
        })
        print(b)
        # robot_status_all1_req

    def test_rbklib_1100(self):
        r = rbklib.Rbklib("192.168.8.255")
        while True:
            try:
                time.sleep(5)
                a, b = r.robot_status_all1_req()
                print(b.count())
            except Exception as e:
                print(e)

        # robot_status_all1_req

    def test_rbklib_emc(self):
        r = rbklib.Rbklib("192.168.198.146")
        a, b = r.robot_other_softemc_req(True)
        print(b)

    def test_19301(self):
        r = rbklib.Rbklib("192.168.17.73",push_flag=True)
        a=r.pushData.get()
        ro = RobotPush
        b = ro(**json.loads(a))
        print(b.model_dump())

if __name__ == '__main__':
    unittest.main()

import unittest
from src.pack import packTask as packTask
from src.type.mode import PackMode
from src.type.VDA5050 import order
from src.config.config import Config
from src.serve.robot import Robot
from src.rbklib.rbklibPro import Rbk


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_pask(self):
        o = packTask.PackTask('FORKLIFT')
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../../VDAExample/order")

        json_filename = 'Transport Order.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
            task,uuids = o.pack(order.Order(**json_content), 0)
            print(f"打包结果：{len(task)},{json.dumps(task)}",uuids)

    def test_pask_straight_fork(self):
        o = packTask.PackTask('FORKLIFT') #  CARRIER
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../../VDAExample/order/fork")

        json_filename = 'Transport Order 3066 straight_fork.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
            task,uuids = o.pack(order.Order(**json_content), 'FORKLIFT')
            print(f"打包结果：{len(task)},-----{json.dumps(task)}-----",uuids)

    def test_pask_straight_jack(self):
        o = packTask.PackTask('CARRIER') #  CARRIER
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../../VDAExample/order/jack")

        json_filename = 'Transport Order 3066 straight_jack.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
            task,uuids = o.pack(order.Order(**json_content), 'CARRIER')
            print(f"打包结果：{len(task)},-----{json.dumps(task)}-----",uuids)

    def test_pask_CubicBeizer2(self):
        o = packTask.PackTask('CARRIER') #  CARRIER
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../../VDAExample/order")

        json_filename = 'Transport Order 3066 CubicBeizer2.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
            task,uuids = o.pack(order.Order(**json_content), 'CARRIER')
            print(f"打包结果：{len(task)},-----{json.dumps(task)}-----",uuids)

    def test_pask_one_node(self):
        o = packTask.PackTask(PackMode.params)
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../../VDAExample")

        json_filename = 'Transport Orde one Node.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
            task = o.pack(order.Order(**json_content))
            print(f"打包结果：{json.dumps(task)}")

    def test_pask_mappoint1(self):
        """测试站点导航的pack"""
        c = Config()
        rbk = Rbk(c.robot_ip)
        r = Robot(rbk)
        o = packTask.PackTask(c)
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../../VDAExample/order/mapPoint/")

        json_filename = 'mapPiont_1.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
            task = o.pack(order.Order(**json_content), r)
            print(f"打包结果：{json.dumps(task)}")



if __name__ == '__main__':
    unittest.main()
trajectory = \
    {
        "NURBS": {
            "trajectory": {
                "type": "NURBS",
                "degree": 1,
                "knotVector": [0, 0, 1, 1],
                "controlPoints": [
                    {
                        "x": 0.0,
                        "y": 0.0,
                        "weight": 1
                    },
                    {
                        "x": 12.5,
                        "y": 1.5,
                        "weight": 1
                    }
                ]
            }
        },
        "Straight": {
            "trajectory": {
                "type": "Straight",
                "controlPoints": [
                    {
                        "x": 12.5,
                        "y": 1.5,
                    },
                    {
                        "x": 12.5,
                        "y": 1.5,
                    }
                ]
            }
        },
        "CubicBeizer": {
            "trajectory": {
                "type": "CubicBeizer",
                "controlPoints": [
                    {
                        "x": 20,
                        "y": 1.5,
                    },
                    {
                        "x": 20,
                        "y": 1.5,
                    },
                    {
                        "x": 40,
                        "y": 2.5,
                    },
                    {
                        "x": 40,
                        "y": 2.5,
                    }
                ]
            }
        }
    }

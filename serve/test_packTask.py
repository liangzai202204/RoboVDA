import unittest
import packTask as packTask
from type.mode import PackMode
from type.VDA5050 import order


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_pask(self):
        o = packTask.PackTask('script.py')
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")

        json_filename = 'Transport Order.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
            task,uuids = o.pack(order.Order(**json_content),0)
            print(f"打包结果：{len(task)},{json.dumps(task)}",uuids)




    def test_pask_one_node(self):
        o = packTask.PackTask(PackMode.params)
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")

        json_filename = 'Transport Orde one Node.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
            task = o.pack(order.Order(**json_content))
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

import unittest
import OrderStateMachine as om
from type import order, pushMsgType


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_order_machine(self):
        o = om.OrderStateMachine()
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")

        json_filename = 'Transport Order.json'

        json_file_path = os.path.join(path_to_B, json_filename)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)
            print(json_content)
            o.add_order(order.Order(**json_content))
            print(o.nodes)
            print(o.edges)
            print(o.actions)
            s = pushMsgType.TaskStatusPackage(**{
                "task_status_list": [
                    {
                        "status": 3,
                        "task_id": "758de28a-c7f6-4475-b623-c4c895780b26",
                        "type": 0
                    },
                    {
                        "status": 4,
                        "task_id": "20cd999e-6159-4d58-8a40-4d8fc08f3e1f",
                        "type": 0
                    }]
            })
            o.update_order_status(s)
            print("-=" * 20)
            print(o.nodes)
            print(o.edges)
            print(o.actions)


if __name__ == '__main__':
    unittest.main()

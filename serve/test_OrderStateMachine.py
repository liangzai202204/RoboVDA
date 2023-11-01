import unittest
import OrderStateMachine as om
from type import order, pushMsgType,instantActions


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
            o.add_order(order.Order(**json_content),True)
            print(o.nodes)
            print(o.edges)
            print(o.actions)
            s = pushMsgType.TaskStatusPackage(**{
                "task_status_list": [
                    {
                        "status": 4,
                        "task_id": "758de28a-c7f6-4475-b623-c4c895780b26",
                        "type": 0
                    },
                    {
                        "status": 4,
                        "task_id": "20cd999e-6159-4d58-8a40-4d8fc08f3e1f",
                        "type": 0
                    },
                    {
                        "status": 4,
                        "task_id": "215a13b2-2aa7-42e6-9882-938a16b15f6e",
                        "type": 0
                    }
                ]
            })
            o.update_order_status(s,1)
            # 添加 instantAction
            import json
            import os
            # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
            path_to_B = os.path.abspath("../VDAExample")

            json_filename = 'startPaues Order InstantAction.json'

            json_file_path = os.path.join(path_to_B, json_filename)

            with open(json_file_path, 'r') as json_file:
                json_content = json.load(json_file)
                print(json_content)
            instant_action = instantActions.InstantActions(**json_content)
            for ins in instant_action.instantActions:
                o.add_instant_action(ins)

            print("-=" * 20)
            s = pushMsgType.TaskStatusPackage(**{
                "task_status_list": [
                    {
                        "status": 4,
                        "task_id": "758de28a-c7f6-4475-b623-c4c895780b26",
                        "type": 0
                    },
                    {
                        "status": 4,
                        "task_id": "20cd999e-6159-4d58-8a40-4d8fc08f3e1f",
                        "type": 0
                    },
                    {
                        "status": 3,
                        "task_id": "215a13b2-2aa7-42e6-9882-938a16b15f6e",
                        "type": 0
                    }

                ]
            })
            o.update_order_status(s,3)
            print(o.get_order_status())
            self.assertIsNotNone(o.actions,"action empty")
            self.assertIsNotNone(o.instant_actions,"instant_actions empty")

    def test_order_machine_one_node(self):
        """測試只有一個 node
        1、測試 order
        2、測試 instantAction

        :return:
        """
        o = om.OrderStateMachine()
        import json
        import os
        # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
        path_to_B = os.path.abspath("../VDAExample")

        json_filename = 'Transport Orde one Node.json'

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
                        "status": 1,
                        "task_id": "20cd999e-6159-4d58-8a40-4d8fc08f3e1f",
                        "type": 0
                    }
                ]
            })
            o.update_order_status(s,6)
            # 添加 instantAction
            import json
            import os
            # 假设包 B 的名称为 package_B，JSON 文件名为 data.json
            path_to_B = os.path.abspath("../VDAExample")

            json_filename = 'startPaues Order InstantAction.json'

            json_file_path = os.path.join(path_to_B, json_filename)

            with open(json_file_path, 'r') as json_file:
                json_content = json.load(json_file)
                print(json_content)
            instant_action = instantActions.InstantActions(**json_content)
            for ins in instant_action.instantActions:
                o.add_instant_action(ins)

            o.update_order_status(s, 3)
            print("-=" * 20)
            print("节点",o.nodes)
            print("边",o.edges)
            print("动作",o.actions)
            print("瞬时动作",o.instant_actions)

            self.assertIsNot(o.nodes,"node empty")
            self.assertIsNot(o.edges,"edge empty")
            self.assertIsNot(o.actions,"action empty")
            self.assertIsNotNone(o.instant_actions,"instant_actions empty")


if __name__ == '__main__':
    unittest.main()

import unittest
import asyncio
import unittest
import uuid
import json
import uuid
import paho.mqtt.client as mqtt
from serve.handle_topic import RobotOrder
from type import order
from log.log import MyLogger
import state


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_node_position(self):
        a = {
            "allowedDeviationTheta": 1.0,
            "allowedDeviationXY": 0.0,
            "mapDescription": "Description of Map",
            "mapId": "9b270f29-262e-4b74-b90b-0faee129d00e",
            "theta": -3.140000104904175,
            "x": 10.119999885559082,
            "y": 27.0
        }
        a_s = state.NodePosition(**a)
        b = {
            "allowedDeviationTheta": 1.0,
            "allowedDeviationXY": 0.0,
            "mapDescription": "Description of Map",
            "mapId": "9b270f29-262e-4b74-b90b-0faee129d00e",
            "theta": -3.140000104904175,
            "x": 10.119999885559082,
            "y": 27.0
        }
        b_s = state.NodePosition(**b)
        c = {
            "allowedDeviationTheta": 1.1,
            "allowedDeviationXY": 0.0,
            "mapDescription": "Description of Map",
            "mapId": "9b270f29-262e-4b74-b90b-0faee129d00e",
            "theta": -3.140000104904175,
            "x": 10.119999885559082,
            "y": 27.0
        }
        c_s = state.NodePosition(**c)
        self.assertEqual(a_s, b_s)
        self.assertNotEqual(a_s, c_s)


if __name__ == '__main__':
    unittest.main()

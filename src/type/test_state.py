import unittest
from typing import List

import pydantic

from src.type.VDA5050 import state


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

    def test_Task(self):
        import socket

        so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        so.bind(("", 32323))
        while True:
            msg, (ip, port) = so.recvfrom(1024)
            print(f"IP:{ip}, PORT:{port}, MSG:{msg.decode('utf-8')}")


if __name__ == '__main__':
    class E(pydantic.BaseModel):
        s: List[{str: str}]


    a = E(s=[{"4": "4"}])
    print(a)

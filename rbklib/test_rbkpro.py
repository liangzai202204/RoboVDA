import unittest
import rbklibPro


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_init(self):
        r = rbklibPro.Rbk("192.168.0.107")
        while True:
            pass



if __name__ == '__main__':
    unittest.main()

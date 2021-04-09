import logging
import unittest

from src.helpers import chrono

logging.basicConfig(level=logging.DEBUG)

class Test_Chrono(unittest.TestCase):
    def test_chrono(self):
        f = Foo()
        self.assertLogs(f.foo(100))

class Foo():
    @chrono.chrono
    def foo(self, num: int):
        for _i in range(num):
            pass

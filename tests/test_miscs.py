#! /usr/bin/env python3
# coding: utf-8

import logging
import unittest

import numpy
from src.helpers.chrono import chrono

logging.basicConfig(level=logging.DEBUG)


class Test_Miscs(unittest.TestCase):
    def test_perf_tuple_array(self):
        @chrono
        def test_array(count):
            a = [[1, 2, 3]]
            for i in range(count):
                b = a[0][0]
                c = a[0][2]

        @chrono
        def test_tuple(count):
            a = [[1, 2, 3]]
            a[0] = tuple(a[0])
            a = tuple(a)
            for i in range(count):
                b = a[0][0]
                c = a[0][2]

        @chrono
        def test_numpy(count):
            a = numpy.zeros((1, 3))
            a[0] = [1, 2, 3]
            for i in range(count):
                b = a[0, 0]
                c = a[0, 2]

        count = 1 #100_000_000
        test_array(count)
        test_tuple(count)
        test_numpy(count)

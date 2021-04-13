#! /usr/bin/env python3
# coding: utf-8

import logging
import unittest
import timeit

import numpy
from src.helpers.chrono import chrono
from src.helpers.area   import Area, IndexedArea

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

    def test_coords(self):
        @chrono
        def test_area(count, area):
            for _i in range(count):
                for _x, _y in area:
                    pass

        @chrono
        def test_index_area(count, area):
            for _i in range(count):
                for i in area:
                    _x = area.convert_x(i)
                    _y = area.convert_y(i)
                    pass
        
        @chrono
        def test_index(count, area):
            for _n in range(count):
                size = max(area.width, area.height)
                invert = size == area.height
                for i in range(area.surface):
                    _x = i % size if invert else int(i / size)
                    _y = int(i / size) if invert else i % size
                    pass
            
        count = 5
        logging.debug("Converted Index")
        test_index(count, Area(300, 300))
        logging.debug("Indexed Area")
        test_index_area(count, IndexedArea(300, 300))
        logging.debug("Area")
        test_area(count, Area(300, 300))
        
    def test_array_reshape(self):
        a = [1, 2, 3, 4, 5, 6]
        logging.debug(a)
        b = numpy.array(a)
        b = b.reshape([2, 3])
        logging.debug(b)

    def test_list(self):
        number = 1000
        # Creation 1D array
        # logging.debug("for loop:" + str(timeit.timeit("[0.0 for x in range(300*300)]", number=number))) #> 7.58s
        logging.debug("array init:" + str(timeit.timeit("[0.0] * (300*300)", number=number))) #> 0.21s
        logging.debug("numpy:" + str(timeit.timeit("numpy.zeros(300*300, numpy.float64)", "import numpy", number=number))) #> 0.028s

        # Creation 2D array
        logging.debug("array 2d init:" + str(timeit.timeit("[[0.0] * 300] * 300", number=number))) #> 0.0022s >>> BEST
        logging.debug("numpy 2d:" + str(timeit.timeit("numpy.zeros((300,300), numpy.float64)", "import numpy", number=number))) #> 0.028s

        # Access and data manipulation
        number = 200
        s1 = """
for i in range(len(a)):
    x = int(i / 300)
    y = i % 300
    v = a[i]"""
        s1s="""a = [0.0] * (300*300)"""
        logging.debug("array 1d access:" + str(timeit.timeit(s1, s1s, number=number))) #> 7.25s
        s2 = """
for i in range(len(a)):
    x = int(i / 300)
    y = i % 300
    v = a[i]"""
        s2s="""
import numpy
a = numpy.zeros(300*300, numpy.float64)"""
        logging.debug("numpy 1d access:" + str(timeit.timeit(s2, s2s, number=number))) #> 8.90s
        s3 = """
for x in range(300):
    for y in range(300):
        v = a[x][y]"""
        s3s = """a = [[0.0] * 300] * 300"""
        logging.debug("array 2d access:" + str(timeit.timeit(s3, s3s, number=number))) #> 2.69s >>> BEST
        s4 = """
for x in range(300):
    for y in range(300):
        v = a[x, y]"""
        s4s = """
import numpy
a = numpy.zeros((300,300), numpy.float64)"""
        logging.debug("numpy 2d access:" + str(timeit.timeit(s4, s4s, number=number))) #> 4.73s

    def test_func_call(self):
        number = 100000
        s1 = """pass"""
        s2 = """f()"""
        s2s = """
def f():
    pass"""
        logging.debug("without func: " + str(timeit.timeit(s1, number=number)))     #> 0.0075s >>> BEST
        logging.debug("with func: " + str(timeit.timeit(s2, s2s, number=number)))   #> 0.26s

    def test_map(self):
        number = 10000
        s1s = """a = [1] * 1000
def add(v):
    return v + v"""
        s1 = """
for i in range(len(a)):
    a[i] = add(i)"""
        logging.debug("for loop: " + str(timeit.timeit(s1, s1s, number=number)))     #> 18.13s
        s2s = """a = [1] * 1000
def add(v):
    return v + v"""
        s2 = """a = map(add, a)"""
        logging.debug("map func: " + str(timeit.timeit(s2, s2s, number=number)))     #> 0.0031s >>> BEST

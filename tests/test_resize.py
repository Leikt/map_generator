#! /usr/bin/env python3
# coding: utf-8

import unittest

import numpy
from src.helpers.resize import resize_data


class Test_Resize(unittest.TestCase):
    def test_resize_2D(self):
        arr = numpy.zeros((10, 20))
        for x in range(10):
            for y in range(20):
                arr[x, y] = x + y
    
        arr_resized, w, h = resize_data(arr, 10, 20, 2)
        self.assertEqual(w, 20)
        self.assertEqual(h, 40)

        self.assertEqual(arr[0, 0], arr_resized[0, 0])
        self.assertEqual(arr[0, 0], arr_resized[1, 0])
        self.assertEqual(arr[0, 0], arr_resized[1, 1])
        self.assertEqual(arr[0, 0], arr_resized[0, 1])
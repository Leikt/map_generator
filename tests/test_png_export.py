#! /usr/bin/env python3
# coding: utf-8

import unittest

import numpy
import src.exporters.png as png


class Test_PNGRenderer(unittest.TestCase):
    def test_2d_data(self):
        width = 10
        height = 15
        data = numpy.zeros((width, height))
        data[0, 0] = 0.5
        data[0, 1] = 0.66  # Bottom is lighter
        data[1, 0] = 0.33  # Right is darker
        png.export(
            "tests/outputs/png_renderer_bw.png", width, height, data)

    def test_3d_data(self):
        width = 10
        height = 15
        data = numpy.zeros((width, height, 3))
        data[0, 0] = [0, 1, 0]
        data[0, 1] = [1, 0, 0]  # Bottom is Red
        data[1, 0] = [0, 0, 1]  # Right is Blue
        png.export(
            "tests/outputs/png_renderer_color.png", width, height, data)

    def test_error(self):
        data = numpy.zeros(10)
        self.assertRaises(ValueError, png.export,
                          "blabla", 10, 0, data)

    def test_raw(self):
        data = numpy.zeros((10, 15, 3), numpy.uint8)
        for x in range(10):
            for y in range(15):
                data[x, y] = [12, x * 10, 233]
        png.exportRaw("tests/outputs/png_renderer_raw.png", data, rotate=True)

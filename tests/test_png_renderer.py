#! /usr/bin/env python3
# coding: utf-8

import unittest

import numpy
import src.rendering.png_renderer as png_renderer


class Test_PNGRenderer(unittest.TestCase):
    def test_2d_data(self):
        width = 10
        height = 15
        data = numpy.zeros((height, width))
        data[0, 0] = 1.0
        data[0, 1] = 0.66  # Y, X
        data[1, 0] = 0.33
        png_renderer.render(
            "tests/outputs/png_renderer_bw.png", width, height, data)

    def test_3d_data(self):
        width = 10
        height = 15
        data = numpy.zeros((height, width, 3))
        data[0, 0] = [0, 1, 0]
        data[0, 1] = [1, 0, 0]
        data[1, 0] = [0, 0, 1]
        png_renderer.render(
            "tests/outputs/png_renderer_color.png", width, height, data)

    def test_error(self):
        data = numpy.zeros(10)
        self.assertRaises(ValueError, png_renderer.render,
                          "blabla", 10, 0, data)

    def test_raw(self):
        data = numpy.zeros((15, 10, 3), numpy.uint8)
        for x in range(10):
            for y in range(15):
                data[y, x] = [12, x*10, 233]
        png_renderer.renderRaw("tests/outputs/png_renderer_raw.png", data)

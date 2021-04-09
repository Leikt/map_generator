#! /usr/bin/env python3
# coding: utf-8

import unittest

from src.helpers.area import Area


class Test_Area(unittest.TestCase):
    def test_coordinates(self):
        area = Area(5, 10)
        self.assertEqual(area.surface, 5 * 10)
        self.assertEqual(area.width, 5)
        self.assertEqual(area.height, 10)
        minX = maxX = minY = maxY = counter = 0
        for x, y in area:
            minX = min(x, minX)
            minY = min(y, minY)
            maxX = max(x, maxX)
            maxY = max(y, maxY)
            counter += 1
        self.assertEqual(minX, 0)
        self.assertEqual(minY, 0)
        self.assertEqual(maxX, 4)
        self.assertEqual(maxY, 9)
        self.assertEqual(counter, area.surface)

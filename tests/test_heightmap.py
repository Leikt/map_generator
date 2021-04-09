#! /usr/bin/env python3
# coding: utf-8

import unittest

from src.heightmap import Heightmap


class Test_Heightmap(unittest.TestCase):
    def test_heightmap(self):
        heightmap = Heightmap(10, 20)
        counter = 0
        for x, y in heightmap.coordinates:
            counter += 1
            heightmap[x, y] = x + y
        self.assertEqual(counter, heightmap.surface)
        self.assertEqual(heightmap[4, 6], 4 + 6)

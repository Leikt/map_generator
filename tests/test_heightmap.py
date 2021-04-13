#! /usr/bin/env python3
# coding: utf-8

import unittest

from src.raw.heightmap import Heightmap


class Test_Heightmap(unittest.TestCase):
    def test_heightmap(self):
        heightmap = Heightmap(10, 20)
        counter = 0
        for x, y in heightmap.coordinates:
            counter += 1
            heightmap[x, y] = x + y
        heightmap[5, 7] = 3
        self.assertEqual(counter, heightmap.surface)
        self.assertEqual(heightmap[4, 6], 4 + 6)
        self.assertEqual(heightmap.lowest, 0)
        self.assertEqual(heightmap.highest, 9 + 19)
        self.assertEqual(heightmap[5, 7], 3)
        np_arr = heightmap.to_numpy()
        self.assertTrue(np_arr[0, 0] == 0 and heightmap[0, 0] == 0)
        self.assertTrue(np_arr[0, 1] == 1 and heightmap[0, 1] == 1)
        self.assertTrue(np_arr[5, 7] == 3 and heightmap[5, 7] == 3)


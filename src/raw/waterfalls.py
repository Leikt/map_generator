#! /usr/bin/env python3
# coding: utf-8

import logging
import numpy
from src.raw.rawmap import RawMap

class Waterfalls():

    @property
    def waterfalls(self):
        """Access the waterfalls property"""
        return self._waterfalls

    def __init__(self, rawmap: RawMap, map_width: int, map_height: int):
        self._rawmap = rawmap
        self._map_width = map_width
        self._map_height = map_height

    def calculate_waterfalls(self):
        # Retrieve working variables
        rivermap = self._rawmap.rivermap
        cliffmap = self._rawmap.cliffs
        map_width, map_height = self._map_width, self._map_height

        # Init result
        waterfalls = numpy.zeros((map_width, map_height), numpy.float64)

        # Test each cliff if there is a river on it
        for x in range(map_width):
            for y in range(map_height):
                if cliffmap[x, y] > 0 and rivermap[x, y] > 0:
                    waterfalls[x, y] = cliffmap[x, y]
        
        # Set the waterfall result
        self._waterfalls = waterfalls
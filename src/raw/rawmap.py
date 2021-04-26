#! /usr/bin/env python3
# coding: utf-8

import numpy


class RawMap:
    """Class that contains raw map data
    Parameters
    ==========
        width: int
    Map width
        height: int
    Map height"""

    def __init__(self, width: int, height: int):
        self.working_width = int(width / 2)
        self.working_height = int(height / 2)
        self.final_width = self.width = self.working_width * 2
        self.final_height = self.height = self.working_height * 2
        self.heightmap = numpy.zeros((1, 1), numpy.float64)
        self.stratums = numpy.zeros((1, 1), numpy.float64)
        self.cliffs = numpy.zeros((1, 1), numpy.uint8)
        self.rivermap = numpy.zeros((1, 1), numpy.float64)
        self.poolmap = numpy.zeros((1, 1), numpy.float64)
        self.waterfallmap = numpy.zeros((1, 1), numpy.float64)

    @staticmethod
    def from_array(arr: list) -> object:
        """Create a RawMap from the given array
        Parameters
        ==========
            arr: list
        [width, height, heightmap, stratums, cliffs, rgb_cliffs]
        Returns
        =======
            RawMap"""

        # No list > No Raw Map
        if arr is None:
            return None
        # Setup the rawmap
        rm = RawMap(arr[0], arr[1])
        rm.heightmap = arr[2]
        rm.stratums = arr[3]
        rm.cliffs = arr[4]
        rm.rivermap = arr[5]
        rm.poolmap = arr[6]
        rm.waterfallmap = arr[7]
        # Return the result
        return rm

    def to_array(self) -> list:
        """Convert itself into an array that can be used as a RawMap.from_array argument
        Returns
        =======
            list"""

        return [self.width, self.height, self.heightmap, self.stratums, self.cliffs, self.rivermap, self.poolmap, self.waterfallmap]

    def clone(self) -> object:
        """Make a clone of the RawMap and all its arrays"""

        rawmap = RawMap(self.width, self.height)
        rawmap.heightmap = numpy.copy(self.heightmap)
        rawmap.stratums = numpy.copy(self.stratums)
        rawmap.cliffs = numpy.copy(self.cliffs)
        rawmap.rivermap = numpy.copy(self.rivermap)
        rawmap.poolmap = numpy.copy(self.poolmap)
        rawmap.waterfallmap = numpy.copy(self.waterfallmap)
        return rawmap
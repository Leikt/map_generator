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
        self.width = width
        self.height = height
        self.heightmap = numpy.zeros((width, height), numpy.float64)
        self.stratums = numpy.zeros((width, height), numpy.float64)
        self.cliffs = numpy.zeros((width, height), numpy.uint8)
        self.rgb_cliffs = numpy.zeros((width, height, 3), numpy.uint8)

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
        rm.rgb_cliffs = arr[5]
        # Return the result
        return rm

    def to_array(self) -> list:
        """Convert itself into an array that can be used as a RawMap.from_array argument
        Returns
        =======
            list"""

        return [self.width, self.height, self.heightmap, self.stratums, self.cliffs, self.rgb_cliffs]

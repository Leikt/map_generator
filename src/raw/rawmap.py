#! /usr/bin/env python3
# coding: utf-8

import numpy

class RawMap:
    """Class that contains raw map data"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.heightmap = numpy.zeros((width, height), numpy.float64)
        self.level_curves = numpy.zeros((width, height), numpy.float64)

    @staticmethod
    def from_array(arr: list):
        # No list > No Raw Map
        if arr is None:
            return None
        # Setup the rawmap
        rm = RawMap(arr[0], arr[1])
        rm.heightmap = arr[2]
        # Return the result
        return rm

    def to_array(self):
        return [self.width, self.height, self.heightmap]

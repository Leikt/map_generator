#! /usr/bin/env python3
# coding: utf-8

import numpy

from src.helpers.area import Area

class Heightmap():
    """Class that manage a heightmap"""

    def __init__(self, width, height):
        self._area = Area(width, height)
        # self._data = numpy.zeros(
        #     (self._area.height, self._area.width), numpy.float64)
        self._data = [[0.0 for j in range(height)] for i in range(width)]


    def __getitem__(self, key: tuple) -> float:
        """Return the height at the given coordinates"""
        return self._data[key[0]][key[1]]

    def __setitem__(self, key: tuple, value: float):
        """Set the height at the given coordinates"""
        self._data[key[0]][key[1]] = value

    @property
    def coordinates(self) -> object:
        """Return the iterable coordinates"""
        return self._area

    @property
    def surface(self):
        """Access the surface property"""
        return self._area.surface

    @property
    def width(self):
        """Access the width property"""
        return self._area.width

    @property
    def height(self):
        """Access the height property"""
        return self._area.height

    @property
    def lowest(self):
        """Access the lowest property"""
        return numpy.amin(self._data)

    @property
    def highest(self):
        """Access the highest property"""
        # return numpy.amax(self._data)
        return numpy.amax(self._data)

    def to_numpy(self):
        """Convert the heightmap to a array numpy
        Returns
        =======
            numpy.array
        The array"""

        # return numpy.copy(self._data)
        return numpy.array(self._data, numpy.float64)
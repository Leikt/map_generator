#! /usr/bin/env python3
# coding: utf-8

import numpy

from src.area import Area

class Heightmap():
    """Class that manage a heightmap"""

    def __init__(self, width, height):
        self._area = Area(width, height)
        self._data = numpy.zeros(
            (self._area.width, self._area.height), numpy.float64)

    def __getitem__(self, key: tuple) -> float:
        """Return the height at the given coordinates"""
        return self._data[key]

    def __setitem__(self, key: tuple, value: float):
        """Set the height at the given coordinates"""
        self._data[key] = value

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

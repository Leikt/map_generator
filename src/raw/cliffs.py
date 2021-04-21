#! /usr/bin/env python3
# coding: utf-8

import logging

import numpy
from src.helpers.chrono import chrono


class Cliffs():
    """Class that process the stratums into a cliff map
    Parameters
    ==========
        parameters: object
    A SimpleNamespace object with attributes (sea Parameters.parameters)
        stratums: object
    Numpy 2D array that contains height data
        width: int
    Width of the map
        height: int
    Height of the map
    Parameters.parameters
    =====================
        None for now"""

    DIRS_OFFSETS = [(0, -1), (1, -1), (1, 0), (1, 1),
                    (0, 1), (-1, 1), (-1, 0), (-1, -1)]

    NORTH_MASK = 0b1100_0001
    SOUTH_MASK = 0b0001_1100
    EAST_MASK = 0b0111_0000
    WEST_MASK = 0b0000_0111
    ALL_MASKS = [NORTH_MASK, EAST_MASK, SOUTH_MASK, WEST_MASK]

    def __init__(self, parameters: object, stratums: object, width: int, height: int):
        self._parameters = parameters
        self._stratums = stratums
        self._width = width
        self._height = height

    @property
    def cliffs(self):
        """Access the cliffs property"""
        return self._cliffs

    @chrono
    def calculate_cliffs(self):
        """Process throug the stratums and calculate the cliff code"""

        self._cliffs = cliffs = numpy.zeros((self._width, self._height))
        if (numpy.amax(self._stratums) == numpy.amin(self._stratums)):
            return  # Flatland
        # Wrok variables
        dirs_offsets = self.DIRS_OFFSETS
        map_width = self._width
        map_height = self._height
        stratums = self._stratums
        # Calculate each cliff orientation
        for x in range(map_width):
            for y in range(map_height):
                current_height = stratums[x, y]
                current = 0
                for dir_x, dir_y in dirs_offsets:
                    nx, ny = x + dir_x, y + dir_y
                    current = current << 1
                    if 0 <= nx < map_width and 0 <= ny < map_height:
                        gradient = stratums[nx, ny] - current_height
                        if gradient < 0:
                            current |= 1
                # if current == 0:
                #     current = 0x100
                cliffs[x, y] = current
        self._cliffs = cliffs

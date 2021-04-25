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

    CLIFF_TO_DIR_VECTOR = {
        NORTH_MASK: (0, -1, 0),
        EAST_MASK: (1, 0, 0),
        SOUTH_MASK: (0, 1, 0),
        WEST_MASK: (-1, 0, 0)
    }

    @staticmethod
    def dir_vector(value: int) -> tuple:
        """Convert the cliff value into a direction vector
        Parameters
        ==========
            value: int
        A cliff value
        Returns
        =======
            tuple: [dx, dy, is_inner] where is_inner is 1 is the angle is a inner angle
            None: if the cliff code doesn't exists"""
        
        return Cliffs.CLIFF_TO_DIR_VECTOR.get(value, None)

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
        """Process through the stratums and calculate the cliff code"""

        self._cliffs = cliffs = numpy.zeros((self._width, self._height), numpy.int64)
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

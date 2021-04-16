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
                if current == 0:
                    current = 0x100
                cliffs[x, y] = current
        self._cliffs = cliffs

    @chrono
    def to_rgb_cliff(self, cliffs: object, map_width: int, map_height: int) -> object:
        """Convert the given cliffs to a preview in RGB
        Parameters
        ==========
            cliffs: object
        Numpy 2D array that contains cliff data
            map_width: int
        Width of the map
            map_height: int
        Height of the map
        Returns
        =======
            Numpy 3D array (width, height, 3) ready to be rendered"""

        rgb_cliff = numpy.zeros((map_width, map_height, 3), numpy.uint8)
        mid = int(255 / 2)
        north_mask = 0b1000_0000
        south_mask = 0b0000_1000
        east_mask = 0b0010_0000
        west_mask = 0b0000_0010
        for x in range(map_width):
            for y in range(map_height):
                current = int(cliffs[x, y])
                gradient_north = mid if (current & north_mask) != 0 else 0
                gradient_south = mid if (current & south_mask) != 0 else 0
                gradient_east = mid if (current & east_mask) != 0 else 0
                gradient_west = mid if (current & west_mask) != 0 else 0
                rgb_cliff[x, y] = [
                    mid + gradient_east - gradient_west,
                    mid + gradient_north - gradient_south,
                    mid
                ]
        return rgb_cliff

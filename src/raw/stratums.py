#! /usr/bin/env python3
# coding: utf-8

import logging

import numpy
from src.helpers.chrono import chrono


class Stratums():
    """Class that calculate the stratums of the heightmap.
    Parameters
    ==========
        parameters: object
    A SimpleNamespace object with attributes (sea Parameters.parameters)
        heightmap: object
    A numpy 2d array that contains all the heights of the map
        width: int
    Width of the 2d array
        height: int
    Height of the 2d array
    Parameters.parameters
    =====================
        step_count: int
    The number of stratum in the map. This will define the height of each stratum."""

    DIRS_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                    (0, 1), (1, -1), (1, 0), (1, 1)]
    DIRS_4_OFFSETS = [(-1, 0), (0, -1), (0, 1), (1, 0)]

    def __init__(self, parameters: object, heightmap: object, width: int, height: int):
        self._parameters = parameters
        self._heightmap = heightmap
        self._width = width
        self._height = height

    @property
    def stratums(self):
        """Access the stratums property"""
        return self._stratums

    @chrono
    def calculate_stratums(self):
        """Calculate the stratums"""

        # Retrieve paramters
        try:
            step_count = self._parameters.step_count
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))
        # Init and optimize
        self._stratums = stratums = numpy.zeros(
            (self._width, self._height), numpy.float64)
        heightmap = self._heightmap
        step = (numpy.amax(heightmap) - numpy.amin(heightmap)) / \
            float(step_count)
        if step == 0:
            return  # Flatland
        # Calculate step
        # Calculate the level curve
        self._base_calculation(heightmap, stratums, step)
        # Correct the broken curves
        self._correct_broken_lines(stratums, step, step_count)
        # Correct orphan pixels
        self._correct_orphan_pixels(stratums, step)
        # Store result
        self._stratums = stratums

    def _base_calculation(self, heightmap, stratums: object, step: float):
        for x in range(self._width):
            for y in range(self._height):
                # Exceed is the amount of "mater" over the last startum : we want only the height
                exceed = heightmap[x, y] % step
                stratums[x, y] = heightmap[x, y] - exceed

    def _correct_broken_lines(self, stratums, step, step_count):
        # Init and optimize
        highest = numpy.amax(stratums)
        dirs_offsets = self.DIRS_OFFSETS
        width = self._width
        height = self._height
        filter_range = 0.1 * step
        # We process one stratum at the time because a higher stratum can
        # influence the lowers
        for i in range(step_count + 1):
            # Because we are using float (there aren't a exact science)
            # We need to filter them. It's okay because there is big gaps between stratums
            filter_height = highest - step * i
            for x in range(width):
                for y in range(height):
                    current = stratums[x, y]
                    # If the current height is the one we are processing
                    if filter_height - filter_range < current < filter_height + filter_range:
                        # Check in each direction if there is a big cliff
                        # We want cliff that are the size of a step
                        for dir_x, dir_y in dirs_offsets:
                            nx, ny = x + dir_x, y + dir_y
                            if 0 <= nx < width and 0 <= ny < height:  # It's in the map
                                gradient = current - stratums[nx, ny]
                                if gradient > step:
                                    stratums[nx, ny] = current - step

    def _correct_orphan_pixels(self, stratums, step):
        dirs_offsets = self.DIRS_4_OFFSETS
        map_width = self._width
        map_height = self._height
        for x in range(map_width):
            for y in range(map_height):
                current = stratums[x, y]
                orphan = True
                for dx, dy in dirs_offsets:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < map_width and 0 <= ny < map_height:
                        if stratums[nx, ny] == current:
                            orphan = False
                if orphan:
                    value = 0
                    for dx, dy in dirs_offsets:
                        value += stratums[x + dx, y + dy]
                    value /= 4
                    value -= value % step
                    stratums[x, y] = value
                
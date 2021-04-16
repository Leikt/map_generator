#! /usr/bin/env python3
# coding: utf-8

import numpy
import logging

from src.helpers.chrono import chrono


class Stratums():

    DIRS_OFFSETS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

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
        # Retrieve paramters
        try:
            step_count = self._parameters.step_count
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))
        # Init and optimize
        self._stratums = stratums = numpy.zeros((self._width, self._height), numpy.float64)
        heightmap = self._heightmap
        step = (numpy.amax(heightmap) - numpy.amin(heightmap)) / float(step_count)
        if step == 0:
            return # Flatland
        # Calculate step
        # Calculate the level curve
        self._base_calculation(heightmap, stratums, step)
        # Correct the broken curves
        self._correct_broken_lines(stratums, step, step_count)
        # Store result
        self._stratums = stratums

    def _base_calculation(self, heightmap, stratums: object, step: float):
        for x in range(self._width):
            for y in range(self._height):
                exceed = heightmap[x, y] % step
                stratums[x, y] = heightmap[x, y] - exceed

    def _correct_broken_lines(self, stratums, step, step_count):
        highest = numpy.amax(stratums)
        dirs_offsets = self.DIRS_OFFSETS
        width = self._width
        height = self._height
        filter_range = 0.1 * step
        for i in range(step_count + 1):
            filter_height = highest - step * i
            for x in range(width):
                for y in range(height):
                    current = stratums[x, y]
                    if filter_height - filter_range < current < filter_height + filter_range:
                        for dir_x, dir_y in dirs_offsets:
                            nx, ny = x + dir_x, y + dir_y
                            if 0 <= nx < width and 0 <= ny < height:
                                gradient = current - stratums[nx, ny]
                                if gradient > step:
                                    stratums[nx, ny] = current - step
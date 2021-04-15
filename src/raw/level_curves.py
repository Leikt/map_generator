#! /usr/bin/env python3
# coding: utf-8

import numpy
import logging

class LevelCurves():
    def __init__(self, parameters: object, heightmap: object, width: int, height: int):
        self._parameters = parameters
        self._heightmap = heightmap
        self._width = width
        self._height = height
    
    @property
    def result(self):
        """Access the level curves"""
        return self._result

    def create_level_curves(self):
        # Retrieve paramters
        try:
            step_count = self._parameters.step_count
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))
        # Init and optimize
        level_curves = numpy.zeros((self._width, self._height), numpy.float64)
        heightmap = self._heightmap
        heighest = numpy.amax(heightmap)
        lowest = numpy.amin(heightmap)
        step = (heighest - lowest) / float(step_count)
        # Calculate step
        # Calculate the level curve
        for x in range(self._width):
            for y in range(self._height):
                exceed = heightmap[x, y] % step
                level_curves[x, y] = heightmap[x, y] - exceed
        # Store result
        self._result = level_curves
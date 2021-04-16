#! /usr/bin/env python3
# coding: utf-8

import logging
import random

import numpy
from src.raw.rawmap import RawMap


class Waters():

    DIRS_OFFSETS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def __init__(self, parameters: object, rawmap: RawMap, seed: int):
        try:
            self._rawmap = rawmap
            self._prng = random.Random(seed)
            self._sources = parameters.sources
            self._max_lifetime = parameters.max_lifetime
            self._spawn_range_x = parameters.range_x
            self._spawn_range_y = parameters.range_y
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))
    
    @property
    def water_map(self):
        """Access the water_map property"""
        return self._water_map

    def generate(self):
        # Initialize and optimize
        water_map = numpy.zeros((self._rawmap.width, self._rawmap.height, 3))
        heightmap = self._rawmap.heightmap
        map_width = self._rawmap.width
        map_height = self._rawmap.height
        range_x = (self._spawn_range_x[0] * map_width, self._spawn_range_x[1] * map_width)
        range_y = (self._spawn_range_y[0] * map_height, self._spawn_range_y[1] * map_height)
        prng = self._prng
        # Generate each water source
        for _ in range(self._sources):
            # Spawn random resurgence in the map
            pos_x = prng.randint(*range_x)
            pos_y = prng.randint(*range_y)
            water_map[pos_x, pos_y] = [0, 0, 0.3] # TEMP mark the source
            # Similate the river
            for _a_day_as_a_river_head in range(self._max_lifetime):
                current = heightmap[pos_x, pos_y] + water_map[pos_x, pos_y, 2]
                max_gradient = 0
                new_x, new_y = pos_x, pos_y
                for dx, dy in self.DIRS_OFFSETS:
                    nx, ny = pos_x + dx, pos_y + dy
                    if 0 <= nx < map_width and 0 <= ny < map_height:
                        gradient = current - heightmap[nx, ny] - water_map[nx, ny, 2]
                        if gradient > max_gradient:
                            max_gradient = gradient
                            new_x, new_y = nx, ny

                if pos_x != new_x or pos_y != new_y:
                    # Stop simulating river if it has reached the sea
                    if heightmap[new_x, new_y] == 0:
                        break
                    # Make the river head move
                    pos_x, pos_y = new_x, new_y
                    water_map[pos_x, pos_y] = [0, 0, 0.3]
                else:
                    break
        self._water_map = water_map

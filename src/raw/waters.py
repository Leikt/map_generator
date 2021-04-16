#! /usr/bin/env python3
# coding: utf-8

import logging
import random

import numpy
from src.raw.rawmap import RawMap
from src.helpers.chrono import chrono


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

    @chrono
    def generate(self):
        # Initialize and optimize
        water_map = numpy.zeros((self._rawmap.width, self._rawmap.height, 3))
        heightmap = self._rawmap.heightmap
        map_width = self._rawmap.width
        map_height = self._rawmap.height
        range_x = (self._spawn_range_x[0] * map_width,
                   self._spawn_range_x[1] * map_width)
        range_y = (self._spawn_range_y[0] * map_height,
                   self._spawn_range_y[1] * map_height)
        prng = self._prng
        highest = numpy.amax(heightmap)
        dirs = self.DIRS_OFFSETS
        # Generate each water source
        for _ in range(self._sources):
            # Spawn random resurgence in the map
            pos_x = prng.randint(*range_x)
            pos_y = prng.randint(*range_y)
            water_map[pos_x, pos_y] = [1, 0, 0]  # TEMP mark the source
            # Similate the river
            for _a_day_as_a_river_head in range(self._max_lifetime):
                new_x, new_y = self._water_flow_direction(
                    pos_x, pos_y, heightmap, map_width, map_height)
                if pos_x != new_x or pos_y != new_y:
                    # Stop simulating river if it has reached the sea
                    if heightmap[new_x, new_y] == 0:
                        break
                    # Make the river head move
                    pos_x, pos_y = new_x, new_y
                    water_map[pos_x, pos_y] = [0, 1, 0]
                else:
                    # Lake
                    # Init
                    spillway = None             # Exit of the lake
                    spillway_height = highest   # Height of the exit
                    opened = [(pos_x, pos_y)]   # Nodes to process
                    closed = []  # Node processed
                    counter = 0  # Anti infinite loop
                    # Lake detection loop
                    while len(opened) > 0 and counter < 500:
                        counter += 1
                        # Change the current node to the lowest opened point
                        opened = sorted(
                            opened, key=lambda x: heightmap[x[0], x[1]])
                        current = opened.pop(0)
                        # Close the point so it won't be processed again
                        closed.append(current)
                        current_x, current_y = current
                        # Process the point
                        for dx, dy in dirs:
                            nx, ny = current_x + dx, current_y + dy
                            # If new point is in the map and neither opened or closed
                            if 0 <= nx < map_width and 0 <= ny < map_height and \
                                    not (nx, ny) in opened and not (nx, ny) in closed:
                                nh = heightmap[nx, ny]
                                if nh - heightmap[current_x, current_y] < 0:
                                    # Gradient < 0 tells it a spillway
                                    if spillway_height > nh:
                                        # Change the spillway to the lowest
                                        spillway_height = nh
                                        spillway = (nx, ny)
                                        # Delete opened that are higher than the spillway
                                        opened = list(filter(lambda x: heightmap[x[0], x[1]] <= spillway_height, opened))
                                elif nh <= spillway_height:
                                    # Could be the spillway so we open the node
                                    opened.append((nx, ny))
                    if counter >= 500:
                        logging.warning("Infinite loop...")
                    lake = list(filter(lambda x: heightmap[x[0], x[1]] <= spillway_height, closed))
                    for x, y in lake:
                        water_map[x, y] = [0, 0, 1]
                    if spillway is None:
                        break
                    else:
                        pos_x, pos_y = spillway

        self._water_map = water_map

    def _water_flow_direction(self, pos_x, pos_y, heightmap, map_width, map_height):
        current = heightmap[pos_x, pos_y]
        max_gradient, new_x, new_y = 0, pos_x, pos_y
        for dx, dy in self.DIRS_OFFSETS:
            nx, ny = pos_x + dx, pos_y + dy
            if 0 <= nx < map_width and 0 <= ny < map_height:
                gradient = heightmap[nx, ny] - current
                if gradient < max_gradient:
                    max_gradient = gradient
                    new_x, new_y = nx, ny
        return new_x, new_y

#! /usr/bin/env python3
# coding: utf-8

import logging
import random

import numpy
from src.raw.rawmap import RawMap
from src.helpers.chrono import chrono


class Waters():
    """Class process the water map generation using the heightmap
    Parameters
    ==========
        parameters: object
    A SimpleNamespace object with attributes (sea Parameters.parameters)
        rawmap: RawMap
    The rawmap object
        seed: int
    PRNG seed
    Parameters.parameters
    =====================
        sources: int
    Amount of sources to generate
        max_lifetime: int
    Number of step the river head makes
        range_x: tuple(float,float)
    Range where the sources could appears. In coefficient of the width. Exemple : (0.1, 0.9)
        range_y: tuple(float,float)
    Range where the sources could appears. In coefficient of the height. Exemple : (0.1, 0.9)
        lowest_is_sea: bool
    If true, the simulation will end if the river reach the lowest value of the heightmap
        river_depth: float
    Depth of the river, the higher this value is, the more the river will be able to jump over obstacles but it will reduce the probability of lake
        exclusion_radius: int
    Number of pixel between sources, the generation will try to maintain this distance.
    Raises
    ======
        AttributeError
    If a parameter is missing."""

    DIRS_OFFSETS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def __init__(self, parameters: object, rawmap: RawMap, seed: int):
        try:
            self._rawmap = rawmap
            self._prng = random.Random(seed)
            self._sources = parameters.sources
            self._max_lifetime = parameters.max_lifetime
            self._spawn_range_x = parameters.range_x
            self._spawn_range_y = parameters.range_y
            self._lowest_is_sea = parameters.lowest_is_sea
            self._river_depth = parameters.river_depth
            self._exclusion_radius = parameters.exclusion_radius
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))

    @property
    def water_map(self):
        """Access the water_map property"""
        return self._water_map

    @chrono
    def generate(self):
        """Generate the water map from the given parameters"""

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
        lowest = numpy.amin(heightmap)
        lowest_is_sea = self._lowest_is_sea
        river_depth = self._river_depth
        exclusion_radius = self._exclusion_radius
        sources = []
        # Generate each water source
        for _ in range(self._sources):
            # Spawn random resurgence in the map
            pos_x, pos_y = self._pick_source(sources, prng, range_x, range_y, exclusion_radius)
            sources.append((pos_x, pos_y))
            # Skip the sea sources
            if (heightmap[pos_x, pos_y] == lowest and lowest_is_sea):
                continue
            water_map[pos_x, pos_y] = [river_depth, 0, river_depth]  # TEMP mark the source
            # Similate the river
            for _a_day_as_a_river_head in range(self._max_lifetime):
                new_x, new_y = self._water_flow_direction(
                    pos_x, pos_y, heightmap, map_width, map_height, water_map)
                # Stop simulating river if it has reached the sea
                if lowest_is_sea and heightmap[new_x, new_y] == lowest:
                    break
                # If it has moved : place the river
                if pos_x != new_x or pos_y != new_y:
                    # Make the river head move
                    pos_x, pos_y = new_x, new_y
                # Add the water to the water map
                water_map[pos_x, pos_y, 2] += river_depth
        # Store the result
        self._water_map = water_map

    def _pick_source(self, sources: list, prng: random.Random, range_x: tuple, range_y: tuple, exclusion_radius: int) -> tuple:
        # Optimsation
        prng_randint = prng.randint
        sqr_exclusion = exclusion_radius * exclusion_radius
        # Generate coordinates
        counter = 0
        while counter < 100:
            counter += 1
            # Generate random coodinates
            pos_x = prng_randint(*range_x)
            pos_y = prng_randint(*range_y)
            # Check if the source is far enough the other ones
            valid = True
            for x, y in sources:
                sqr_dst = (x - pos_x) * (x - pos_x) + (y - pos_y) * (y - pos_y)
                if sqr_dst < sqr_exclusion:
                    valid = False
                    break
            # If valide, return it
            if valid:
                return pos_x, pos_y
        return pos_x, pos_y


    def _water_flow_direction(self, pos_x, pos_y, heightmap, map_width, map_height, water_map):
        current = heightmap[pos_x, pos_y] + water_map[pos_x, pos_y, 2]
        max_gradient, new_x, new_y = 0, pos_x, pos_y
        for dx, dy in self.DIRS_OFFSETS:
            nx, ny = pos_x + dx, pos_y + dy
            if 0 <= nx < map_width and 0 <= ny < map_height:
                gradient = heightmap[nx, ny] + water_map[nx, ny, 2] - current
                if gradient < max_gradient:
                    max_gradient = gradient
                    new_x, new_y = nx, ny
        return new_x, new_y
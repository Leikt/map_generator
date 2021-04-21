#! /usr/bin/env python3
# coding: utf-8

import logging
import random

import numpy
from src.raw.rawmap import RawMap
from src.helpers.chrono import chrono
from src.raw.cliffs import Cliffs
import functools


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
    def rivermap(self):
        """Access the water_map property"""
        return self._rivermap

    @property
    def poolmap(self):
        """Access the poolmap property"""
        return self._poolmap

    @chrono
    def generate(self):
        """Generate the water map from the given parameters"""

        # Initialize and optimize
        heightmap = self._rawmap.heightmap
        stratums = self._rawmap.stratums
        cliffmap = self._rawmap.cliffs
        map_width = self._rawmap.width
        map_height = self._rawmap.height
        rivermap = numpy.zeros((map_width, map_height)) # Map of the rivers
        poolmap = numpy.zeros((map_width, map_height)) # Map of the pools
        drains = numpy.full((map_width, map_height, 2), -1) # Map of the drains coordinates
        range_x = (self._spawn_range_x[0] * map_width,
                   self._spawn_range_x[1] * map_width)
        range_y = (self._spawn_range_y[0] * map_height,
                   self._spawn_range_y[1] * map_height)
        prng = self._prng
        lowest = numpy.amin(heightmap) - (0 if self._lowest_is_sea else 1)
        river_depth = self._river_depth
        exclusion_radius = self._exclusion_radius
        sources = []

        # Init pool
        for x in range(map_width):
            for y in range(map_height):
                if stratums[x, y] == lowest:
                    poolmap[x, y] = 0.5

        # Generate each water source
        for _ in range(self._sources):
            # Spawn random resurgence in the map
            pos_x, pos_y = self._pick_source(
                sources, prng, range_x, range_y, exclusion_radius, cliffmap)
            sources.append((pos_x, pos_y))
            # Skip the sea sources
            if (heightmap[pos_x, pos_y] == lowest):
                continue
            rivermap[pos_x, pos_y] = 1  # TEMP mark the source
            path_to_pool = self._find_river(pos_x, pos_y, map_width, map_height, heightmap, stratums, cliffmap, poolmap, drains, lowest)
            for x, y in path_to_pool:
                rivermap[x, y] += 0.5

        # Store the result
        self._rivermap = rivermap
        self._poolmap = poolmap

    def _pick_source(self, sources: list, prng: random.Random, range_x: tuple, range_y: tuple, exclusion_radius: int, cliffmap: object) -> tuple:
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
            if cliffmap[pos_y, pos_y] > 0:
                continue
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

    def _water_flow_direction(self, pos_x, pos_y, heightmap, map_width, map_height, water_map, cliffmap):
        current = heightmap[pos_x, pos_y] + water_map[pos_x, pos_y, 2]
        max_gradient, new_x, new_y = 0, pos_x, pos_y
        for i in range(len(self.DIRS_OFFSETS)):
            dx, dy = self.DIRS_OFFSETS[i]
            cliff_mask = Cliffs.ALL_MASKS[i]
            nx, ny = pos_x + dx, pos_y + dy
            if 0 <= nx < map_width and 0 <= ny < map_height:
                gradient = heightmap[nx, ny] + water_map[nx, ny, 2] - current
                if gradient < max_gradient:
                    if cliffmap[nx, ny] == 0 or \
                            cliffmap[nx, ny] == cliff_mask:
                        max_gradient = gradient
                        new_x, new_y = nx, ny
        return new_x, new_y

    def _find_river(self, x, y, map_width, map_height, heightmap, stratums, cliffmap, poolmap, drains, lowest):
        # Conditions
        def pool_found(pos_x, pos_y):
            return poolmap[pos_x, pos_y] > 0

        def local_lowest_found(pos_x, pos_y):
            for dx, dy in self.DIRS_OFFSETS:
                nx, ny = pos_x + dx, pos_y + dy
                if 0 <= nx < map_width and 0 <= ny < map_height:
                    gradient = heightmap[nx, ny] - heightmap[pos_x, pos_y]
                    if gradient < 0:
                        return False
            return True

        def water_can_flow(pos_x, pos_y, nx, ny):
            gradient_ok = heightmap[nx, ny] - heightmap[pos_x, pos_y] < 0
            cliff_ok = cliffmap[pos_x, pos_y] == 0 or cliffmap[pos_x, pos_y] in Cliffs.ALL_MASKS
            return gradient_ok and cliff_ok

        # Init djikstra algorithm
        weights = numpy.full((map_width, map_height), 2**32) # [opened, closed]
        weights[x, y] = 0
        opened = [(x, y, -1, -1)] # (x, y, prec_x, prec_y)
        closed = []
        found = None
        # Main loop
        while len(opened) > 0 and found is None:
            # Select the node to process
            x, y, px, py = current = min(opened, key=lambda o: o[2])
            opened.remove(current)
            closed.append(current)
            w = weights[x, y]
            # Inspect the neighbours
            for dx, dy in self.DIRS_OFFSETS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < map_width and 0 <= ny < map_height and weights[nx, ny] > w + 1:
                    if pool_found(nx, ny):
                        drain_x, drain_y = drains[nx, ny]
                        if drain_x < 0 or drain_y < 0:
                            # Sea is reached
                            found = [nx, ny, x, y] # pool coords, predec coords
                            print("SEA REACHED : {ll} ".format(ll=found))
                        else:
                            # Flow through the pool directly to the drain
                            opened.append((drain_x, drain_y, x, y))
                            weights[drain_x, drain_y] = w + 1
                    elif local_lowest_found(nx, ny):
                        found = [nx, ny, x, y]
                        print("LOCAL LOWEST : {ll} ".format(ll=found))
                    elif water_can_flow(x, y, nx, ny):
                        opened.append((nx, ny, x, y))
                        weights[nx, ny] = w + 1
        # Processing the results
        if found is None:
            found = [x, y, px, py] # Last node processed
        # Backtracking
        path = [found[0:2]]
        px, py = found[2:4]
        w = weights[found[0], found[1]]
        while w > 0:
            x, y, px, py = tuple(filter(lambda n: n[0] == px and n[1] == py, closed))[0]
            w = weights[x, y]
            path.append((x, y))
        return path
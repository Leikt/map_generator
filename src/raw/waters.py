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
        river_radius: float
    Depth of the river, the higher this value is, the more the river will be able to jump over obstacles but it will reduce the probability of lake
        exclusion_radius: int
    Number of pixel between sources, the generation will try to maintain this distance.
    Raises
    ======
        AttributeError
    If a parameter is missing."""

    DIRS_OFFSETS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    # DIRS_OFFSETS = [(0, -1), (1, 0), (0, 1), (-1, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)]

    def __init__(self, parameters: object, rawmap: RawMap, seed: int):
        try:
            self._rawmap = rawmap
            self._prng = random.Random(seed)
            self._sources = parameters.sources
            self._max_lifetime = parameters.max_lifetime
            self._spawn_range_x = parameters.range_x
            self._spawn_range_y = parameters.range_y
            self._lowest_is_sea = parameters.lowest_is_sea
            self._river_radius = parameters.river_radius
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

    @property
    def waterfallmap(self):
        """Access the waterfallmap property"""
        return self._waterfallmap

    @chrono
    def generate(self):
        """Generate the water map from the given parameters"""

        # Initialize and optimize
        heightmap = self._rawmap.heightmap
        stratums = self._rawmap.stratums
        cliffmap = self._rawmap.cliffs
        map_width = self._rawmap.width
        map_height = self._rawmap.height
        rivermap = numpy.zeros((map_width, map_height))  # Map of the rivers
        poolmap = numpy.zeros((map_width, map_height))  # Map of the pools
        waterfallmap = numpy.zeros((map_width, map_height)) # Map of the waterfalls
        # Map of the drains coordinates
        drains = numpy.full((map_width, map_height, 2), -1)
        range_x = (int(self._spawn_range_x[0] * (map_width - 1)),
                   int(self._spawn_range_x[1] * (map_width - 1)))
        range_y = (int(self._spawn_range_y[0] * (map_height - 1)),
                   int(self._spawn_range_y[1] * (map_height - 1)))
        prng = self._prng
        lowest = numpy.amin(heightmap) - (0 if self._lowest_is_sea else 1)
        lowest_stratum = numpy.amin(stratums) - (0 if self._lowest_is_sea else 1)
        river_radius = self._river_radius
        exclusion_radius = self._exclusion_radius
        sources = []
        rivers = []

        # Init pool with sea

        # Generate each water source
        for i in range(self._sources):
            # Spawn random resurgence in the map
            pos_x, pos_y = self._pick_source(
                sources, prng, range_x, range_y, exclusion_radius, cliffmap, heightmap, lowest)
            sources.append((pos_x, pos_y))
            # Debug
            logging.debug("Source {i} : placed at ({x}, {y})".format(
                i=i, x=pos_x, y=pos_y))
            # Generate river until sea or max depth is reached
            for _ in range(self._max_lifetime):
                # Path to the next local lowest or sea
                river = self._find_river(
                    pos_x, pos_y, map_width, map_height, heightmap, stratums, cliffmap, poolmap, drains, lowest, lowest_stratum)
                # Add the source power to the river
                for x, y in river:
                    rivermap[x, y] += river_radius
                # Store river until final painting
                rivers.append(river)
                pos_x, pos_y = river[-1]
                # Sea -> No more river
                if heightmap[pos_x, pos_y] == lowest:
                    break
                # Local lowest -> let's do some pooling
                drain_found = self._flood(
                    pos_x, pos_y, map_width, map_height, heightmap, cliffmap, poolmap, drains, lowest, stratums, lowest_stratum)
                # The pool is too deep : it is the end of the river
                if not drain_found:
                    logging.debug("No drain found")
                    break
                # Teleport the river next start to the pool drain
                pos_x, pos_y = drains[pos_x, pos_y]
                # If something went wrong and the drain is in a pool -> That's the end of the river
                if poolmap[pos_x, pos_y] > 0 and heightmap[pos_x, pos_y] != lowest:
                    # logging.warning("Something went wrong with the river simulation : drain point ended to be in a pool.")
                    break
        
        # Expend the rivers
        rivermap = self._expend_rivers(rivermap, cliffmap, waterfallmap, rivers, map_width, map_height)

        # Clean river map
        sea_depth = numpy.amax(poolmap)
        for x in range(map_width):
            for y in range(map_height):
                if poolmap[x, y] > 0 or stratums[x, y] == 0:
                    rivermap[x, y] = 0
                # if stratums[x, y] == 0:
                #     poolmap[x, y] = sea_depth
                    poolmap[x, y] = 1
                if rivermap[x, y] > 0:
                    rivermap[x, y] = 1

        # Store the result
        self._rivermap = rivermap
        self._poolmap = poolmap
        self._waterfallmap = waterfallmap

    def _pick_source(self, sources: list, prng: random.Random, range_x: tuple, range_y: tuple, exclusion_radius: int, cliffmap: object, heightmap: object, lowest: float) -> tuple:
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
            # No source directly on cliffs
            if cliffmap[pos_x, pos_y] > 0:
                continue
            # No source in the sea
            if heightmap[pos_x, pos_y] == lowest:
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

    def _find_river(self, x, y, map_width, map_height, heightmap, stratums, cliffmap, poolmap, drains, lowest, lowest_stratum):
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
            gradient_ok = heightmap[nx, ny] - heightmap[pos_x, pos_y] <= 0
            cliff_ok = cliffmap[pos_x, pos_y] == 0 or cliffmap[pos_x,
                                                               pos_y] in Cliffs.ALL_MASKS
            return gradient_ok and cliff_ok

        # Return empty path if pool is found
        if pool_found(x, y):
            return [(x, y)]

        # Init djikstra algorithm
        inf = 2**32
        weights = numpy.full((map_width, map_height), inf)  # [opened, closed]
        weights[x, y] = 0
        opened = [(x, y, -1, -1)]  # (x, y, prec_x, prec_y)
        closed = []
        found = None
        dir_range = range(len(self.DIRS_OFFSETS))
        dirs = self.DIRS_OFFSETS
        # Main loop
        while len(opened) > 0 and found is None:
            # Select the node to process
            x, y, px, py = current = min(opened, key=lambda o: o[2])
            opened.remove(current)
            closed.append(current)
            w = weights[x, y]
            # Inspect the neighbours
            for i in dir_range:
                nx, ny = x + dirs[i][0], y + dirs[i][1]
                if 0 <= nx < map_width and 0 <= ny < map_height and weights[nx, ny] > w + 1:
                    if pool_found(nx, ny) or stratums[nx, ny] == lowest_stratum:
                        drain_x, drain_y = drains[nx, ny]
                        if drain_x < 0 or drain_y < 0:
                            # Sea is reached
                            # pool coords, predec coords
                            found = [nx, ny, x, y]
                        elif weights[drain_x, drain_y] == inf:
                            # Flow through the pool directly to the drain
                            opened.append((drain_x, drain_y, x, y))
                            weights[drain_x, drain_y] = w + 1
                    elif water_can_flow(x, y, nx, ny):
                        opened.append((nx, ny, x, y))
                        weights[nx, ny] = w + 1
                    elif local_lowest_found(nx, ny):
                        found = [nx, ny, x, y]
        # Processing the results
        if found is None:
            found = [x, y, px, py]  # Last node processed
        # Backtracking
        path = [tuple(found[0:2])]
        px, py = found[2:4]
        w = weights[found[0], found[1]]
        while w > 0:
            x, y, px, py = tuple(
                filter(lambda n: n[0] == px and n[1] == py, closed))[0]
            w = weights[x, y]
            path.append((x, y))
        return list(reversed(path))

    @chrono
    def _expend_rivers(self, rivermap, cliffmap, waterfallmap, rivers, map_width, map_height):
        # Init
        expended = numpy.full((map_width, map_height), False, numpy.bool8)
        openend = []
        closed = []
        brush = []
        dirs = self.DIRS_OFFSETS
        dirs_range = range(len(dirs))
        new_rivermap = numpy.zeros((map_width, map_height), numpy.float64)
        # Expend each river
        for river in rivers:
            # Each point of the river including the source
            for x, y in river:
                # If already expended, next
                if expended[x, y]:
                    continue
                expended[x, y] = True
                # Calculate the brush
                openend.clear()
                openend.append((x, y))
                closed.clear()
                brush.clear()
                sqr_radius = rivermap[x, y] * rivermap[x, y]
                # Brush loop
                while len(openend) > 0:
                    current = openend.pop(0)
                    closed.append(current)
                    brush.append(current)
                    for di in dirs_range:
                        nx, ny = current[0] + dirs[di][0], current[1] + dirs[di][1]
                        # Out of the map
                        if not(0 <= nx < map_width and 0 <= ny < map_height):
                            continue
                        # Already closed or openend
                        if (nx, ny) in closed or (nx, ny) in openend:
                            continue
                        # Too far away
                        sqr_dst = (nx - x) * (nx - x) + (ny - y) * (ny - y)
                        if sqr_dst > sqr_radius:
                            continue
                        # Wrong cliff orientation
                        if cliffmap[nx, ny] > 0 and cliffmap[nx, ny] != Cliffs.ALL_MASKS[di]:
                            continue
                        # Add it to the brush
                        openend.append((nx, ny))
                # Apply brush
                weight = rivermap[x, y] / len(brush)
                for bx, by in brush:
                    new_rivermap[bx, by] += weight
        # Update the rivermap
        return new_rivermap

    def _flood(self, pos_x, pos_y, map_width, map_height, heightmap, cliffmap, poolmap, drains, lowest, stratums, lowest_stratum):
        # > Constants
        layer_thickness = 0.005
        layers_number = 100

        # > Init 
        # Layer managment
        layer_counter = 0
        layer = []
        plane = base_plane = heightmap[pos_x, pos_y] + poolmap[pos_x, pos_y]
        tried = numpy.full((map_width, map_height), False, numpy.bool8)
        # Position
        i_pos_x, i_pos_y = pos_x, pos_y
        drain_x = drain_y = None
        # Main loop conditions
        drain_found = False
        layer_limit_reached = layers_number <= 0
        highest = numpy.amax(heightmap)

        # > Main loop
        while not drain_found and not layer_limit_reached:
            # Update layer counter
            layer_counter += 1
            layer_limit_reached = layer_counter > layers_number
            if layer_limit_reached:
                logging.debug("Layers numbres limit reached")
            # Prepare the layer
            base_plane = plane
            plane += layer_thickness
            layer.clear()
            tried.fill(False)
            # Find the layer points from the origin
            opened_x = [i_pos_x]
            opened_y = [i_pos_y]
            tried[i_pos_x, i_pos_y] = True
            # Until there is no potential layer point left
            while len(opened_x) > 0:
                # Retrieve current point and add it to the layer
                x = opened_x.pop()
                y = opened_y.pop()
                layer.append((x, y))
                # Test all the neighbour to if :
                # - One is the drain
                # - There are pool part
                for dx, dy in self.DIRS_OFFSETS:
                    nx, ny = x + dx, y + dy
                    # Out of bound
                    if not(0 <= nx < map_width and 0 <= ny < map_height):
                        continue
                    # Tried already
                    if tried[nx, ny]:
                        continue
                    # Make sure the point won't be tested again
                    tried[nx, ny] = True
                    # It's a drain point or sea
                    if heightmap[nx, ny] + poolmap[nx, ny] < base_plane or stratums[nx, ny] == lowest_stratum:
                        # No concurency -> just set the drain
                        # New drain -> check if this is a lower drain
                        if not drain_found or heightmap[drain_x, drain_y] > heightmap[nx, ny]:
                            drain_x, drain_y = nx, ny
                        # However, the drain is found
                        drain_found = True
                    # It's a pool part if it's neither drain, wall or cliff
                    elif heightmap[nx, ny] < plane and cliffmap[nx, ny] == 0:
                        opened_x.append(nx)
                        opened_y.append(ny)
            
            # Fill the layer
            for x, y in layer:
                poolmap[x, y] = plane - heightmap[x, y]
            # Drain found -> Setup the drain teleportation
            if drain_found:
                # Drain found
                # Fill the layer with drain's height and set the drain map
                drain = (drain_x, drain_y)
                for x, y in layer:
                    drains[x, y] = drain

        # > Result
        # True if the pool has a drain, false if not
        return drain_found
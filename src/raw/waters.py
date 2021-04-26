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

    DIR_4_OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    @property
    def rivermap(self):
        """Access the rivermap property"""
        return self._rivermap

    @property
    def poolmap(self):
        """Access the poolmap property"""
        return self._poolmap

    def __init__(self, parameters: object, rawmap: RawMap, map_width: int, map_height: int, seed: int):
        try:
            self._rawmap = rawmap
            self._prng = random.Random(seed)
            self._river_lifetime = parameters.river_lifetime
            self._sea_level = parameters.sea_level
            sources = parameters.sources
            self._sources_amount = sources.amount
            self._sources_distance = sources.distance
            self._sources_power_range = sources.power_range
            self._sources_x_range = sources.x_range
            self._sources_y_range = sources.y_range
            self._sources_height_range = sources.height_range
            pooling = parameters.pooling
            self._pooling_layer_size = pooling.layer_size
            self._pooling_max_depth = pooling.max_depth
            self._basin_trim = pooling.basin_trim
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))
        else:
            # Store parameters
            self._map_width, self._map_height = map_width, map_height
            # Initialize the parameters if none is missing
            self._sources_x_range = [int(v * self._map_width) for v in self._sources_x_range]
            self._sources_y_range = [int(v * self._map_height) for v in self._sources_y_range]
            lowest = numpy.amin(self._rawmap.heightmap)
            delta_height = numpy.amax(self._rawmap.heightmap) - lowest
            self._sources_height_range = [lowest + v * delta_height for v in self._sources_height_range]
            self._sea_level = lowest + self._sea_level * delta_height
            self._basin_trim = lowest + self._basin_trim * delta_height

    @chrono
    def generate(self):
        # Retrieve work variables
        map_width, map_height = self._map_width, self._map_height

        # Initialize results variables
        rivermap = numpy.zeros((map_width, map_height))
        poolmap = numpy.zeros((map_width, map_height))

        # Initialize work variables
        sources = []  # Sources coordinates
        drainsmap = numpy.full((map_width, map_height), None) # None if no drain, (drain x, drain y) if there is one

        # Generate the rivers and pools on a raw heightmap
        for _ in range(self._sources_amount):
            # Find a valid source
            source, source_power = self._find_source(sources)
            sources.append(source)
            # Simulate the river from this source
            rivermap, poolmap, drainsmap = self._simulate_river(source, source_power, rivermap, poolmap, drainsmap)

        # Draw the final rivers
        # SKIPPED -> The result isn't good enough
        # rivermap = self._draw_final_river(rivermap)

        # Clean the river and poolmap
        rivermap, poolmap = self._clean_waters(rivermap, poolmap)

        # Store the results
        self._rivermap = rivermap
        self._poolmap = poolmap

    def _find_source(self, sources: list[tuple[int, int]]) -> list[tuple[int, int], float]:
        # Retrieve working variables
        map_width, map_height = self._map_width, self._map_height
        heightmap = self._rawmap.heightmap
        cliffmap = self._rawmap.cliffs
        range_x = self._sources_x_range
        range_y = self._sources_y_range
        height_min, height_max = self._sources_height_range
        randint = self._prng.randint
        dst_min = self._sources_distance * self._sources_distance
        dst_diag = map_width * map_width + map_height * map_height
        power_range = self._sources_power_range

        # Init
        x, y = None, None
        source_power = power_range[0] + self._prng.random() * (power_range[1] - power_range[0])

        # Main loop
        # Search random coordinates that are valid or take the last one
        for _ in range(100):  # Max attempt
            # Pick a random cooridnate in the spawn range
            x, y = randint(*range_x), randint(*range_y)
            # Check height
            if not(height_min <= heightmap[x, y] <= height_max):
                continue
            # Check cliff
            if cliffmap[x, y] != 0:
                continue
            # Check distance from other source
            current_min_dst = dst_diag
            for other_x, other_y in sources:
                sqr_dst = (x - other_x) * (x - other_x) + (y - other_y) * (y - other_y) 
                if sqr_dst < current_min_dst:
                    current_min_dst = sqr_dst
            if current_min_dst < dst_min:
                continue
            # Return valid coordinate
            return (x, y), source_power

        # Return the last coordinates tested
        logging.debug("No valid source have been fined.")
        return (x, y), source_power

    def _simulate_river(self, source: tuple[int, int], source_power: float, rivermap: numpy.array, poolmap: numpy.array, drainsmap: numpy.array) -> list[numpy.array, numpy.array, numpy.array]:
        # Optimize function calling
        sea_level = self._sea_level
        heightmap = self._rawmap.heightmap
        lifetime = self._river_lifetime
        flood = self._flood
        find_river = self._find_river
        draw_line_river = self._draw_line_river

        # Init variables
        life = 0
        too_deep_pool = False
        x, y = source

        # Main loop
        # Until sea, pool with no drain or max lifetime reached
        while not too_deep_pool and heightmap[x, y] > sea_level and life < lifetime:
            # Update lifetime
            life += 1
            # River
            river = find_river(x, y, drainsmap)
            # Thin river
            draw_line_river(rivermap, river, source_power)
            # Update the river head position
            x, y = drainsmap[x, y] if drainsmap[x, y] is not None else river[-1]
            # Filling the basin
            poolmap, drainsmap, too_deep_pool = flood(x, y, poolmap, drainsmap)
            # Update position if not too deep
            if not too_deep_pool:
                x, y = drainsmap[x, y]
        # Debug
        if life >= lifetime:
            logging.debug("A river doesn't reach the sea from {s}".format(s=source))
        elif too_deep_pool:
            logging.debug("A pool is too deep")

        # Return the result
        return rivermap, poolmap, drainsmap

    def _flood(self, x: int, y: int, poolmap: numpy.array, drainsmap: numpy.array) -> list[numpy.array, numpy.array, bool]:
        # > Retrieve working variables
        map_width, map_height = self._map_width, self._map_height
        heightmap =self._rawmap.heightmap
        cliffmap = self._rawmap.cliffs
        layer_size = self._pooling_layer_size
        max_depth = self._pooling_max_depth
        sea_level = self._sea_level
        dirs = self.DIR_4_OFFSETS

        # > Init variables
        # Condition
        too_deep = False
        drain_found = False
        # Layer management
        layer = []
        top_plane = bottom_plane = heightmap[x, y] + poolmap[x, y]
        tried = numpy.full((map_width, map_height), False, numpy.bool8)
        # Positions
        i_pos_x, i_pos_y = x, y
        drain_x = drain_y = None

        # Main loop
        # Until max depth reached or drain found
        while not drain_found and not too_deep:
            # Prepare the current layer
            bottom_plane = top_plane
            top_plane += layer_size
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
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    # Out of the map
                    if not(0 <= nx < map_width and 0 <= ny < map_height):
                        continue
                    # Tried already
                    if tried[nx, ny]:
                        continue
                    tried[nx, ny] = True
                    # Cliff are not poolable
                    if cliffmap[nx, ny] != 0:
                        continue
                    # It's a drain point or sea
                    if heightmap[nx, ny] + poolmap[nx, ny] < bottom_plane or heightmap[nx, ny] <= sea_level:
                        # No drain to far -> just set the drain
                        # New drain -> check if this is a lower drain
                        if not drain_found or heightmap[drain_x, drain_y] > heightmap[nx, ny]:
                            drain_x, drain_y = nx, ny
                        # However, the drain is found
                        drain_found = True
                    # It's a pool part if it's neither drain, wall or cliff
                    elif heightmap[nx, ny] < top_plane: #  and cliffmap[nx, ny] == 0:
                        opened_x.append(nx)
                        opened_y.append(ny)

            # Fill the layer
            for x, y in layer:
                poolmap[x, y] = top_plane - heightmap[x, y]
                # Check depth of the pool, if it's to deep : quit
                # This avoid the map to fill up completly
                if poolmap[x, y] > max_depth:
                    too_deep = True

            # Drain found -> Setup the drain teleportation
            if drain_found:
                # logging.debug("Drain found {s}".format(s = (drain_x ,drain_y, heightmap[drain_x, drain_y])))
                # Drain found
                # Fill the layer with drain's height and set the drain map
                drain = (drain_x, drain_y)
                for x, y in layer:
                    drainsmap[x, y] = drain

        # Return the results
        return poolmap, drainsmap, too_deep

    def _find_river(self, i_x: int, i_y: int, drainsmap: numpy.array):
        def node_normal(x, y, found_target, target, nodes, tried, dirs, map_width, map_height, heightmap):
            # Test each neighbours
            for dx, dy in dirs:
                # Neighbour coordinates
                nx, ny = x + dx, y + dy
                # Out of the map
                if not(0 <= nx < map_width and 0 <= ny < map_height):
                    continue
                # Already tried
                if tried[nx, ny]:
                    continue
                tried[nx, ny] = True
                # Sea -> End of the river
                if heightmap[nx, ny] <= sea_level:
                    # logging.debug("A river has reached the sea")
                    found_target = True
                    target = (nx, ny, x, y)
                    break
                # Wall (water can't flow upward)
                elif heightmap[nx, ny] - heightmap[x, y] >= basin_trim:
                    continue
                # Water can flow
                else:
                    point = (nx, ny, x, y)
                    nodes.append(point)
            # Return the results
            return found_target, target

        def node_cliff(x, y, found_target, target):
            # Type of cliff
            cliff_vector = Cliffs.dir_vector(cliffmap[x, y])
            # Unknown cliff
            if cliff_vector is None:
                pass # Water can't flow through that

            # Angle cliff
            elif cliff_vector[0] != 0 and cliff_vector[1] != 0:
                pass # Water can't flow through that

            # Vertical cliff
            elif cliff_vector[0] == 0 and cliff_vector[1] != 0:
                nx, ny = x, y + cliff_vector[1]
                # Out of the map
                if not(0 <= nx < map_width and 0 <= ny < map_height):
                    return found_target, target
                # Already tried
                if tried[nx, ny]:
                    return found_target, target
                tried[nx, ny] = True
                # Sea -> End of the river
                if heightmap[nx, ny] <= sea_level:
                    # logging.debug("A river has reached the sea")
                    found_target = True
                    target = (nx, ny, x, y)
                    return found_target, target
                # Wall (water can't flow upward)
                elif heightmap[nx, ny] - heightmap[x, y] >= basin_trim:
                    return found_target, target
                # Water can flow
                else:
                    point = (nx, ny, x, y)
                    nodes.append(point)

            # Lateral cliff
            elif cliff_vector[0] != 0 and cliff_vector[1] == 0:
                # TODO Sideway waterfall tiles
                # When the tiles are created we will know how they works exaclty
                # and what space do they need
                pass
            
            return found_target, target

        # Retrieve working variables
        map_width, map_height = self._map_width, self._map_height
        dirs = self.DIR_4_OFFSETS
        heightmap = self._rawmap.heightmap
        cliffmap = self._rawmap.cliffs
        sea_level = self._sea_level
        basin_trim = self._basin_trim

        # Init variables
        nodes = [(i_x, i_y, None, None)] # x, y, previous x, previous y
        tried = numpy.full((map_width, map_height), False, numpy.bool8)
        tried[i_x, i_y] = True
        closed = []
        found_target = False
        target = None
        
        # Main loop : 
        # Optimized djikstra pathfinding
        while not found_target and len(nodes) > 0:
            # Set the current to the lowest node
            x, y, px, py = current = min(nodes, key=lambda p: heightmap[p[0], p[1]])
            nodes.remove(current)
            closed.append(current)
            # Change coordinates if there is a drain
            if drainsmap[x, y] is not None:
                # logging.debug("A river join a pool")
                x, y = drainsmap[x, y]
                current = (x, y, px, py)
                closed.append(current)
            # Test the node
            if cliffmap[x, y] != 0:
                # Cliff node
                found_target, target = node_cliff(x, y, found_target, target)
            else:
                # Normal node
                found_target, target = node_normal(x, y, found_target, target, nodes, tried, dirs, map_width, map_height, heightmap)

        # Process the results
        # Target not found : take the lowest point in closed that is not on a cliff
        if not found_target:
            potential = list(filter(lambda p: cliffmap[p[0], p[1]] == 0, closed))
            if len(potential) == 0:
                return [(i_x, i_y)]
            target = min(potential, key=lambda p: heightmap[p[0], p[1]])
            found_target = True
        # Backtrack the path
        river = [target[:2]] # Init the last point of the river
        previous = target[2:4] # Init the backtrace
        # Backtrack to the starting point
        while previous[0] is not None:
            point = tuple(filter(lambda n: n[0] == previous[0] and n[1] == previous[1], closed))[0]
            river.append(point[:2])
            previous = point[2:4]
        river = list(reversed(river))

        # Return the result
        return river

    def _draw_line_river(self, rivermap: numpy.array, river: list[tuple[int, int]], source_power: float):
        for x, y in river:
            rivermap[x, y] += source_power
        return rivermap

    @chrono
    def _draw_final_river(self, rivermap: numpy.array) -> numpy.array:
        # Retrieve work variables
        map_width, map_height = self._map_width, self._map_height
        dirs = self.DIR_4_OFFSETS
        cliffmap = self._rawmap.cliffs

        # Init result
        new_rivermap = numpy.zeros((map_width, map_height), numpy.float64)

        # Main loop
        for x in range(map_width):
            for y in range(map_height):
                # Only process the rivers
                if rivermap[x, y] == 0:
                    continue
                # Create the brush
                river_power = rivermap[x, y]
                sqr_radius = river_power * river_power 
                opened = [(x, y)]
                brush = []
                # Brush loop
                while len(opened) > 0:
                    current = opened.pop(0)
                    brush.append(current)
                    # Inspect neighbours
                    for dx, dy in dirs:
                        nx, ny = current[0] + dx, current[1] + dy
                        # Out of the map
                        if not(0 <= nx < map_width and 0 <= ny < map_height):
                            continue
                        # Already in the brush
                        if (nx, ny) in brush:
                            continue
                        # To far away
                        sqr_dst = (x - nx) * (x - nx) + (y - ny) * (y - ny) 
                        if sqr_dst > sqr_radius:
                            continue
                        # Wrong cliff
                        if cliffmap[nx, ny] > 0:
                            cliff_vector = Cliffs.dir_vector(cliffmap[x, y])
                            if cliff_vector is None:
                                continue
                            elif cliff_vector[0] != 0 or cliff_vector[1] == 0:
                                continue
                        # In the brush
                        opened.append((nx, ny))
                # Apply river
                weight = river_power / len(brush)
                for bx, by in brush:
                    new_rivermap[bx, by] += weight

        # Return the painted rivers
        return new_rivermap

    def _clean_waters(self, rivermap: numpy.array, poolmap: numpy.array) -> list[numpy.array, numpy.array, numpy.array]:
        # Retrieve work variables
        map_width, map_height = self._map_width, self._map_height
        stratums = self._rawmap.stratums
        cliffmap = self._rawmap.cliffs
        lowest = numpy.amin(stratums) - (1 if self._sea_level < numpy.amin(self._rawmap.heightmap) else 0)

        # Main loop
        for x in range(map_width):
            for y in range(map_height):
                if stratums[x, y] < lowest:
                    poolmap[x, y] = rivermap[x, y] = 0
                elif stratums[x, y] == lowest:
                    poolmap[x, y] = 1
                    rivermap[x, y] = 0
                elif poolmap[x, y] > 0:
                    rivermap[x, y] = 0
                    poolmap[x, y] = 1
                elif rivermap[x, y] > 0:
                    rivermap[x, y] = 1
        return rivermap, poolmap
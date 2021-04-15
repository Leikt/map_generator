#! /usr/bin/env python3
# coding: utf-8

import math
import random
import numpy
import logging

from src.helpers.chrono import chrono


class Erosion():
    # def __init__(self, heightmap: object, *, width: int, height: int, seed: int, brush_radius: int,
    #              inertia: float, sediment_capacity_factor: float, sediment_min_capacity: float,
    #              erode_speed: float, deposit_speed: float, evaporate_speed: float, gravity: float,
    #              droplet_lifetime: float, droplets: int, initial_water_volume: float, initial_speed: float, sea_level: float,
    #              **unused):
    def __init__(self, parameters: object, heightmap: object, width: int, height: int, seed: int):
        try:
            self._heightmap = heightmap
            self._width = width
            self._height = height
            self._prng = random.Random(seed)
            self._droplets_amount = parameters.droplets
            self._brush_radius = parameters.brush_radius
            self._inertia = parameters.inertia
            self._sediment_capacity_factor = parameters.sediment_capacity_factor
            self._sediment_min_capacity = parameters.sediment_min_capacity
            self._erode_speed = parameters.erode_speed
            self._deposit_speed = parameters.deposit_speed
            self._evaporate_speed = parameters.evaporate_speed
            self._gravity = parameters.gravity
            self._droplet_lifetime = parameters.droplet_lifetime
            self._initial_water = parameters.initial_water_volume
            self._initial_speed = parameters.initial_speed
            self._sea_level = parameters.sea_level
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))
        
    @chrono
    def init_brushes(self):
        """Initialize the erosion brushes. This long method is optimized to minimize the call to function"""

        # Initialize work variables
        radius = self._brush_radius
        width = self._width
        height = self._height
        weight_sum = 0
        add_index = 0
        brush_template = self._brush_template(radius)
        offsets_x = numpy.zeros(len(brush_template))
        offsets_y = numpy.zeros(len(brush_template))
        weights = numpy.zeros(len(brush_template))
        # Final brushes data
        brushes_ox = numpy.full((width, height), object)
        brushes_oy = numpy.full((width, height), object)
        brushes_we = numpy.full((width, height), object)

        # Create the brush for each cell
        for x in range(width):
            for y in range(height):
                # The brush change if the cell is near the borders
                if (y <= radius or y >= height - radius or x <= radius + 1 or x >= width - radius):
                    weight_sum = 0
                    add_index = 0
                    for ox, oy, weight in brush_template:
                        coord_x = x + ox
                        coord_y = y + oy
                        if coord_x >= 0 and coord_x < width and coord_y >= 0 and coord_y < height:
                            offsets_x[add_index] = ox
                            offsets_y[add_index] = oy
                            weights[add_index] = weight
                            weight_sum += weight
                            add_index += 1
                # Set the brush
                # Note that add_index and all the variables only changes when the brush
                # is near a border
                num_entries = add_index
                brushes_ox[x, y] = [None] * num_entries
                brushes_oy[x, y] = [None] * num_entries
                brushes_we[x, y] = [None] * num_entries
                for i in range(num_entries):
                    brushes_ox[x, y][i] = int(x + offsets_x[i])
                    brushes_oy[x, y][i] = int(y + offsets_y[i])
                    brushes_we[x, y][i] = weights[i] / weight_sum

        # Save brushes in the erosion object
        self._brushes_ox = brushes_ox
        self._brushes_oy = brushes_oy
        self._brushes_we = brushes_we

    def _brush_template(self, radius: int) -> tuple:
        """Create the template for the circular brush
        Parameters
        ==========
            radius: int
        The radius of the brush
        Returns
        =======
            tuple ((offset_x, offset_y, weight))
        The tuple of tuples (offset_x, offset_y, weight)"""

        # Work variable
        brush_template = []
        # Optimization
        push_brush_template = brush_template.append
        math_sqrt = math.sqrt
        for x in range(-radius, radius):
            for y in range(-radius, radius):
                sqr_dst = x * x + y * y
                # Only put in the tuple the coords that are in the radius
                if sqr_dst < radius:
                    push_brush_template(
                        (x, y, 1 - math_sqrt(sqr_dst) / radius))
        return tuple(brush_template)

    @chrono
    def erode(self):
        """Simulate a large amount of water droplets progressivly eroding the heightmap."""

        # Note: this method can't afford to call functions, this is why it's so long : optimization

        # Initialize work variables
        heightmap = self._heightmap
        initial_speed = self._initial_speed
        initial_water = self._initial_water
        width = self._width
        height = self._height
        droplet_max_lifetime = self._droplet_lifetime
        inertia = self._inertia
        sea_level = self._sea_level
        sediment_capacity_factor = self._sediment_capacity_factor
        sediment_min_capacity = self._sediment_min_capacity
        deposit_speed = self._deposit_speed
        erode_speed = self._erode_speed
        brushes_ox = self._brushes_ox
        brushes_oy = self._brushes_oy
        brushes_we = self._brushes_we
        gravity = self._gravity
        evaporate_factor = 1 - self._evaporate_speed
        log_step = 5_000
        next_log = log_step
        # Optimization
        rand_pos = self._prng.randint
        height_and_gradient = self._calculate_height_and_gradient
        math_sqrt = math.sqrt

        for droplet in range(self._droplets_amount):
            # Log progress
            if droplet == next_log:
                next_log += log_step
                logging.debug("{d} of {n} ({p}%)".format(
                    d=droplet, n=self._droplets_amount, 
                    p=round(10000 * droplet/self._droplets_amount) / 100))
            # Initialize droplet
            pos_x = rand_pos(0, width - 2)
            pos_y = rand_pos(0, height - 2)
            dir_x = 0
            dir_y = 0
            speed = initial_speed
            water = initial_water
            sediment = 0
            # Simulate the droplet
            for _a_day_as_a_droplet in range(droplet_max_lifetime):
                # > Move the droplet
                cell_x = int(pos_x)
                cell_y = int(pos_y)
                # Calculate droplet's offset inside the cell (0,0) = at NW node, (1,1) = at SE node
                cell_offset_x = pos_x - cell_x
                cell_offset_y = pos_y - cell_y
                # Calculate droplet's height and direction of flow with bilinear interpolation of surrounding heights
                droplet_height, gradient_x, gradient_y = height_and_gradient(
                    heightmap, width, height, pos_x, pos_y)
                # Update the droplet's direction and position (move position 1 unit regardless of speed)
                dir_x = (dir_x * inertia - gradient_x * (1 - inertia))
                dir_y = (dir_y * inertia - gradient_y * (1 - inertia))
                # Normalize direction
                length = math_sqrt(dir_x * dir_x + dir_y * dir_y)
                if (length != 0):
                    dir_x /= length
                    dir_y /= length
                pos_x += dir_x
                pos_y += dir_y
                # Stop simulating droplet if it's not moving or has flowed over edge of map
                if ((dir_x == 0 and dir_y == 0) or pos_x < 1 or pos_x >= width - 2 or pos_y < 1 or pos_y >= height - 2):
                    break
                # Find the droplet's new height and calculate the deltaHeight
                new_droplet_height = height_and_gradient(
                    heightmap, width, heightmap, pos_x, pos_y)[0]
                delta_height = new_droplet_height - droplet_height
                # Stop simulating droplet if it's fallen into the sea
                if (sea_level != None and new_droplet_height <= sea_level):
                    break
                # > Erode the heightmap
                # Calculate the droplet's sediment capacity (higher when moving fast down a slope and contains lots of water)
                sediment_capacity = max(-delta_height * speed * water *
                                        sediment_capacity_factor, sediment_min_capacity)
                # If carrying more sediment than capacity, or if flowing uphill:
                if (sediment > sediment_capacity or delta_height > 0):
                    # If moving uphill (deltaHeight > 0) try fill up to the current height, otherwise deposit a fraction of the excess sediment
                    amount_to_deposit = None
                    if (delta_height > 0):
                        amount_to_deposit = min(delta_height, sediment)
                    else:
                        amount_to_deposit = (
                            sediment - sediment_capacity) * deposit_speed
                    sediment -= amount_to_deposit
                    # Add the sediment to the four nodes of the current cell using bilinear interpolation
                    #  Deposition is not distributed over a radius (like erosion) so that it can fill small pits
                    heightmap[cell_x, cell_y] += amount_to_deposit * \
                        (1 - cell_offset_x) * (1 - cell_offset_y)
                    heightmap[cell_x + 1, cell_y] += amount_to_deposit * \
                        cell_offset_x * (1 - cell_offset_y)
                    heightmap[cell_x, cell_y + 1] += amount_to_deposit * \
                        (1 - cell_offset_x) * cell_offset_y
                    heightmap[cell_x + 1, cell_y + 1] += amount_to_deposit * \
                        cell_offset_x * cell_offset_y

                else:
                    # Erode a fraction of the droplet's current carry capacity.
                    # Clamp the erosion to the change in height so that it doesn't dig a hole in the terrain behind the droplet
                    amount_to_erode = min(
                        (sediment_capacity - sediment) * erode_speed, -delta_height)

                    # Use erosion brush to erode from all nodes inside the droplet's erosion radius
                    for brush_point_index in range(len(brushes_ox[cell_x, cell_y])):
                        ox = brushes_ox[cell_x, cell_y][brush_point_index]
                        oy = brushes_oy[cell_x, cell_y][brush_point_index]
                        delta_sediment = min(heightmap[ox, oy], amount_to_erode *
                                             brushes_we[cell_x, cell_y][brush_point_index])
                        heightmap[ox, oy] -= delta_sediment
                        sediment += delta_sediment
                # Update droplet's speed and water content
                speed = math_sqrt(
                    max(0, speed * speed + delta_height * gravity))
                water *= evaporate_factor
        # Last droplet debug
        logging.debug("{d} of {n} ({p}%)".format(
            d=self._droplets_amount, n=self._droplets_amount, 
            p=100.00))

    def _calculate_height_and_gradient(self, heightmap: object, width: int, height: int, pos_x: float, pos_y: float) -> tuple:
        """Calculate the height and the gradients of the given point
        Parameters
        ==========
            heightmap: object
        numpy 2D array containing floats
            width: int
        Width of the heightmap
            height: int
        Height of the heightmap
            pos_x: float
        position where to calculate the height and gradient
            pos_y: float
        position where to calculate the height and gradient
        Returns
        =======
            tuple (height, gradient_x, gradient_y)"""

        cell_x = int(pos_x)
        cell_y = int(pos_y)
        # Calculate droplet's offset inside the cell (0,0) = at NW node, (1,1) = at SE node
        x = pos_x - cell_x
        y = pos_y - cell_y
        # Calculate heights of the four nodes of the droplet's cell
        height_nw = heightmap[cell_x, cell_y]
        height_ne = heightmap[cell_x + 1, cell_y]
        height_sw = heightmap[cell_x, cell_y + 1]
        height_se = heightmap[cell_x + 1, cell_y + 1]
        # Calculate droplet's direction of flow with bilinear interpolation of height difference along the edges
        gradient_x = (height_ne - height_nw) * (1 - y) + \
            (height_se - height_sw) * y
        gradient_y = (height_sw - height_nw) * (1 - x) + \
            (height_se - height_ne) * x
        # Calculate height with bilinear interpolation of the heights of the nodes of the cell
        height = height_nw * (1 - x) * (1 - y) + height_ne * x * \
            (1 - y) + height_sw * (1 - x) * y + height_se * x * y
        return (height, gradient_x, gradient_y)

#! /usr/bin/env python3
# coding: utf-8

import math
import random
import numpy
import logging

from src.helpers.chrono import chrono
from src.helpers.area import Area, OffsetedArea
from src.raw.heightmap import Heightmap


LOGGING_STEP = 10_000  # droplets


class HeightAndGradient():
    """Class that containt height and gradients values"""

    @property
    def height(self):
        """Access the height property"""
        return self.__height

    @height.setter
    def height(self, value):
        """Set the height property"""
        self.__height = value

    @property
    def gradient_x(self):
        """Access the gradient_x property"""
        return self.__gradient_x

    @gradient_x.setter
    def gradient_x(self, value):
        """Set the gradient_x property"""
        self.__gradient_x = value

    @property
    def gradient_y(self):
        """Access the gradient_y property"""
        return self.__gradient_y

    @gradient_y.setter
    def gradient_y(self, value):
        """Set the gradient_y property"""
        self.__gradient_y = value

class ErosionBrush():
    def __init__(self, radius):
        # Initialize work variables
        #   Square area used to create the circular brush
        brush_area = OffsetedArea(
            radius * 2, radius * 2, -radius, -radius)
        weight_sum = 0
        sqr_radius = radius ** 2
        self.__brush = []

        # Create the brush
        for x, y in brush_area:
            sqr_dst = x * x + y * y
            if sqr_dst < sqr_radius:
                weight = 1 - math.sqrt(sqr_dst) / radius
                weight_sum += weight
                self.__brush.append([x, y, weight])

        # Correct weights and freeze data
        for i in range(len(self.__brush)):
            self.__brush[i][2] /= weight_sum
            self.__brush[i] = tuple(self.__brush[i])
        # Freeze the brush
        self.__brush = tuple(self.__brush)

    def __iter__(self):
        for brush in self.__brush:
            yield brush

class Erosion():
    def __init__(self, heightmap: Heightmap, *, seed: int, droplets: int, brush_radius: int,
                 inertia: float, sediment_capacity_factor: float,
                 sediment_min_capacity: float, erode_speed: float,
                 deposit_speed: float, evaporate_speed: float,
                 gravity: float, droplet_lifetime: int,
                 initial_water_volume: float, initial_speed: float,
                 sea_level: float, **unused):

        self.__heightmap = heightmap
        self.__prng = random.Random(seed + 1)
        self.__droplets = droplets
        self.__droplet_lifetime = droplet_lifetime
        self.__brush_radius = brush_radius
        self.__sediment_capacity_factor = sediment_capacity_factor
        self.__sediment_min_capacity = sediment_min_capacity
        self.__inertia = inertia
        self.__deposit_speed = deposit_speed
        self.__erode_speed = erode_speed
        self.__evaporate_speed = evaporate_speed
        self.__gravity = gravity
        self.__initial_water_volume = initial_water_volume
        self.__initial_speed = initial_speed
        self.__sea_level = sea_level

    def init_brush(self):
        self.__brush = ErosionBrush(self.__brush_radius)

        # # Initialize work variables
        # #   Square area used to create the circular brush
        # brush_area = OffsetedArea(
        #     self.__brush_radius * 2, self.__brush_radius * 2, -self.__brush_radius, -self.__brush_radius)
        # weight_sum = 0
        # sqr_radius = self.__brush_radius ** 2
        # self.__brush = []

        # # Create the brush
        # for x, y in brush_area:
        #     sqr_dst = x * x + y * y
        #     if sqr_dst < sqr_radius:
        #         weight = 1 - math.sqrt(sqr_dst) / self.__brush_radius
        #         weight_sum += weight
        #         self.__brush.append([x, y, weight])

        # # Correct weights and freeze data
        # for i in range(len(self.__brush)):
        #     self.__brush[i][2] /= weight_sum
        #     self.__brush[i] = tuple(self.__brush[i])
        # # Freeze the brush
        # self.__brush = tuple(self.__brush)

        # # Store attributes in local variables for lisibility
        # width = self.__heightmap.width
        # height = self.__heightmap.height
        # radius = self.__brush_radius

        # # Initialize the attributes
        # self.__brushes_indices = numpy.full((height, width), None, object)
        # self.__brushes_weights = numpy.full((height, width), None, object)

        # # Initialize the working variables
        # offsets = [None for i in range(4 * radius * radius)]
        # weights = [None for i in range(4 * radius * radius)]
        # weight_sum = 0
        # add_index = 0
        # area = Area(width, height)
        # # center_area = OffsetedArea(
        # #     width - radius * 2, height - radius * 2, radius, radius)
        # brush_area = OffsetedArea(radius * 2, radius * 2, -radius, -radius)

        # # Create all brushes
        # for center_x, center_y in area:
        #     # Borders are managed diffently
        #     # if not center_area.valid(center_x, center_y):
        #     if center_y <= radius or center_y >= height - radius or center_x <= radius + 1 or center_x >= width - radius:
        #         weight_sum = 0
        #         add_index = 0
        #         # Each cell in the brush area
        #         for x, y in brush_area:
        #             sqr_dst = x * x + y * y
        #             # Brush are circles
        #             if sqr_dst < radius * radius:
        #                 coord_x = center_x + x
        #                 coord_y = center_y + y
        #                 # If the cell is outside the map, it's not added to the brush
        #                 if area.valid(coord_x, coord_y):
        #                     weight = 1 - math.sqrt(sqr_dst) / radius
        #                     weight_sum += weight
        #                     weights[add_index] = weight
        #                     offsets[add_index] = (x, y)
        #                     add_index += 1
        #     # Update the entries
        #     # Notice that add_index and all working variables are only
        #     # modified when the brush passes on the border cells
        #     # Since first coordinates are (0, 0), the num_entries are always set
        #     num_entries = add_index
        #     # Set the brush data
        #     self.__brushes_indices[center_y, center_x] = [None for i in range(num_entries)]
        #     self.__brushes_weights[center_y, center_x] = [None for i in range(num_entries)]
        #     for i in range(num_entries):
        #         self.__brushes_indices[center_y, center_x][i] = [
        #             center_x + offsets[i][0], center_y + offsets[i][1]]
        #         self.__brushes_weights[center_y,
        #                                center_x][i] = weights[i] / weight_sum

    def erode(self):
        """Repeat the erosion process for the wanted num of time"""
        
        # Init variables
        hag = HeightAndGradient()
        area = Area(self.__heightmap.width, self.__heightmap.height)

        for iteration in range(self.__droplets):
            # Advancement log
            if iteration % LOGGING_STEP == 0:
                self.log_progress(iteration, self.__droplets)
            # Initialize work variables
            pos_x = self.__prng.randint(1, self.__heightmap.width - 2)
            pos_y = self.__prng.randint(1, self.__heightmap.height - 2)
            dir_x = 0
            dir_y = 0
            speed = self.__initial_speed
            water = self.__initial_water_volume
            sediment = 0

            for _a_day_as_a_droplet in range(self.__droplet_lifetime):
                # Initialize droplet
                node_x = int(pos_x)
                node_y = int(pos_y)
                # Calculate droplet's offset inside the cell (0,0) = at NW node, (1,1) = at SE node
                cell_offset_x = pos_x - node_x
                cell_offset_y = pos_y - node_y

                # Calculate droplet's height and direction of flow with bilinear interpolation of surrounding heights
                self.calculate_height_and_gradient(
                    hag, self.__heightmap, pos_x, pos_y)

                # Update the droplet's direction and position (move position 1 unit regardless of speed)
                dir_x = dir_x * self.__inertia - \
                    hag.gradient_x * (1 - self.__inertia)
                dir_y = dir_y * self.__inertia - \
                    hag.gradient_y * (1 - self.__inertia)

                # Normalize direction
                length = math.sqrt(dir_x * dir_x + dir_y * dir_y)
                if (length != 0):
                    dir_x /= length
                    dir_y /= length
                pos_x += dir_x
                pos_y += dir_y

                # Stop simulating droplet if it's not moving or has flowed over edge of map
                if ((dir_x == 0 and dir_y == 0) or pos_x < 1 or pos_x >= self.__heightmap.width - 2 or pos_y < 1 or pos_y >= self.__heightmap.height - 2):
                    break

                # Find the droplet's new height and calculate the delta_height
                new_height = self.calculate_height_and_gradient(
                    None, self.__heightmap, pos_x, pos_y).height
                delta_height = new_height - hag.height

                # Stop simulating droplet if it's fallen into the sea
                if (self.__sea_level != None and new_height <= self.__sea_level):
                    break
                
                # Calculate the droplet's sediment capacity (higher when moving fast down a slope and contains lots of water)
                sediment_capacity = max(-delta_height * speed * water *
                                        self.__sediment_capacity_factor, self.__sediment_min_capacity)

                # If carrying more sediment than capacity, or if flowing uphill:
                if (sediment > sediment_capacity or delta_height > 0):
                    # If moving uphill (delta_height > 0) try fill up to the current height, otherwise deposit a fraction of the excess sediment
                    amount_to_deposit = None
                    if (delta_height > 0):
                        amount_to_deposit = min(delta_height, sediment)
                    else:
                        amount_to_deposit = (
                            sediment - sediment_capacity) * self.__deposit_speed
                    sediment -= amount_to_deposit
                    # Add the sediment to the four nodes of the current cell using bilinear interpolation
                    #  Deposition is not distributed over a radius (like erosion) so that it can fill small pits
                    self.__heightmap[node_x, node_y] += amount_to_deposit * \
                        (1 - cell_offset_x) * (1 - cell_offset_y)
                    self.__heightmap[node_x + 1, node_y] += amount_to_deposit * \
                        cell_offset_x * (1 - cell_offset_y)
                    self.__heightmap[node_x, node_y + 1] += amount_to_deposit * \
                        (1 - cell_offset_x) * cell_offset_y
                    self.__heightmap[node_x + 1, node_y + 1] += amount_to_deposit * \
                        cell_offset_x * cell_offset_y

                else:
                    # Erode a fraction of the droplet's current carry capacity.
                    # Clamp the erosion to the change in height so that it doesn't dig a hole in the terrain behind the droplet
                    amount_to_erode = min(
                        (sediment_capacity - sediment) * self.__erode_speed, -delta_height)

                    # Use erosion brush to erode from all nodes inside the droplet's erosion radius
                    for dx, dy, weight in self.__brush:
                        x = node_x + dx
                        y = node_y + dy
                        # Make sure that the coordinates are in the map
                        if not area.valid(x, y):
                            continue
                        # Calculate sedimeent
                        weighed_erode_amount = amount_to_erode * weight
                        delta_sediment = min(self.__heightmap[x, y], weighed_erode_amount)
                        self.__heightmap[x, y] -= delta_sediment
                        sediment += delta_sediment
                        

                    # # Use erosion brush to erode from all nodes inside the droplet's erosion radius
                    # for brush_point_index in range(len(self.__brushes_indices[node_y, node_x])):
                    #     x, y = self.__brushes_indices[node_y,
                    #                                   node_x][brush_point_index]
                    #     weighed_erode_amount = amount_to_erode * \
                    #         self.__brushes_weights[node_y,
                    #                                node_x][brush_point_index]
                    #     delta_sediment = None
                    #     if (self.__heightmap[x, y] < weighed_erode_amount):
                    #         delta_sediment = self.__heightmap[x, y]
                    #     else:
                    #         delta_sediment = weighed_erode_amount
                    #     self.__heightmap[x, y] -= delta_sediment
                    #     sediment += delta_sediment

                # Update droplet's speed and water content
                speed = math.sqrt(
                    max(0, speed ** 2 + delta_height * self.__gravity))
                water *= (1 - self.__evaporate_speed)
        # Log final advancement
        self.log_progress(self.__droplets, self.__droplets)

    def calculate_height_and_gradient(self, h_and_g: HeightAndGradient, heightmap: Heightmap, pos_x: float, pos_y: float) -> HeightAndGradient:
        """Calculate the height of the point and the gradients in all directions
        Parameters
        ==========
            h_and_g: HeightAndGradient
        The object to edit
            heightmap: Heightmmap
        The heightmap used for calculation
            pos_x: float
        X coordinate
            pos_y: float
        Y coordinate
        Returns
        =======
            HeightAndGradient
        Result of the calculation"""

        h_and_g = HeightAndGradient() if h_and_g is None else h_and_g
        # Cell coordinates
        coord_x, coord_y = int(pos_x), int(pos_y)
        # Calculate droplet's offset inside the cell (0,0) = at NW node, (1,1) = at SE node
        x, y = pos_x - coord_x, pos_y - coord_y
        # Calculate heights of the four nodes of the droplet's cell
        height_nw = heightmap[coord_x, coord_y]
        height_ne = heightmap[coord_x + 1, coord_y]
        height_sw = heightmap[coord_x, coord_y + 1]
        height_se = heightmap[coord_x + 1, coord_y + 1]
        # Calculate droplet's direction of flow with bilinear interpolation of height difference along the edges
        h_and_g.gradient_x = (height_ne - height_nw) * \
            (1 - y) + (height_se - height_sw) * y
        h_and_g.gradient_y = (height_sw - height_nw) * \
            (1 - x) + (height_se - height_ne) * x
        # Calculate height with bilinear interpolation of the heights of the nodes of the cell
        h_and_g.height = height_nw * (1 - x) * (1 - y) + height_ne * x * \
            (1 - y) + height_sw * (1 - x) * y + height_se * x * y
        # Return the result
        return h_and_g

    def log_progress(self, iteration: int, droplets: int):
        percent = round(10000 * iteration / droplets) / 100
        logging.debug("Erosion : {count} droplets of {total} ({percent}%)...".format(
            count=iteration, total=droplets, percent=percent))


@chrono
def erode(heightmap: Heightmap, **kwargs):
    """Drop a certain number or droplets on random places on the given heightmap and mock
    the natural erosion.
    Parameters
    ==========
        heightmap: Heightmap
    The heightmap to erode, will be modified in the process
        seed: int
    The PRNG seed
        droplets: int
    The number of droplets to drop. Affect performance and details of the result.
        radius: int
    The erosion brush radius
        inertia: float
    At zero, water will instantly change direction to flow downhill. At 1, water will never change direction.
        sediment_capacity_factor: float
    Multiplier for how much sediment a droplet can carry
        sediment_min_capacity: float
    Used to prevent carry capacity getting too close to zero on flatter terrain
        erode_speed: float
    Affect the amount of matter eroded when the droplet move
        deposit_speed: float
    Affect the amount of deposit droped by the droplet when it moves
        evaporate_speed: float
    Quantity of water that disapear each iteration of droplet life step
        gravity: float
    Mock the gravity in speed calculation
        initial_water_volume: float
    Initial volume in a droplet
        initial_speed: float
    Initial speed of the droplet, make the process faster
        **unused
    Other unused arguments, hack to use **large_hash when calling this method"""

    if kwargs["droplets"] > 0:
        er = Erosion(heightmap, **kwargs)
        er.init_brush()
        er.erode()
    return heightmap

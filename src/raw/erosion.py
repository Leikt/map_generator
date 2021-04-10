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
        
    def init_brushes(self):
        """Initialize the brushes"""

        # Initialize the attribute
        self.__brushes = numpy.zeros((self.__heightmap.height, self.__heightmap.width, self.__brush_radius * 2, self.__brush_radius * 2))
    
    def erode(self):
        """Repeat the erosion process for the wanted num of time"""
        pass

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

        # Cell coordinates
        coord_x, coord_y = int(pos_x), int(pos_y)
        # Calculate droplet's offset inside the cell (0,0) = at NW node, (1,1) = at SE node
        x, y = pos_x - coord_x, pos_y - coord_y
        # Calculate heights of the four nodes of the droplet's cell
        height_nw = heightmap[coord_y, coord_x]
        height_ne = heightmap[coord_y, coord_x + 1]
        height_sw = heightmap[coord_y - 1, coord_x]
        height_se = heightmap[coord_y - 1, coord_x + 1]
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

    Erosion(heightmap, **kwargs)
    return heightmap

#! /usr/bin/env python3
# coding: utf-8

import math
import random
import numpy

from src.helpers.chrono import chrono
from src.helpers.area import Area
from src.raw.heightmap import Heightmap


@chrono
def erode(heightmap: Heightmap, *, seed: int, droplets: int, radius: int,
          inertia: float, sediment_capacity_factor: float,
          sediment_min_capacity: float, erode_speed: float,
          deposite_speed: float, evaporate_speed: float,
          gravity: float, droplet_liftime: int,
          initial_water_volume: float, initial_speed: float,
          **unused):
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
        deposite_speed: float
    Affect the amount of deposit droped by the droplet when it moves
        evaporate_speed: float
    Quantity of water that disapear each iteration of droplet life step
        initial_water_volume: float
    Initial volume in a droplet
        initial_speed: float
    Initial speed of the droplet, make the process faster
        **unused
    Other unused arguments, hack to use **large_hash when calling this method"""

    # Initialization
    h_and_g = __HeightAndGradient()


def __initialize_brushes(width, height, radius) -> list:
    # Initialize the brush data
    # [y, x] > [coords (list of tuple (x,y)), weights (list of float)]
    erosion_brushes = numpy.full((height, width, 3), None, object)

    # Initialize work variables
    weights_and_offsets = numpy.full((radius * radius * 4), None, object)
    weight_sum = 0
    area = Area(width, height)
    radius_area = Area(2 * radius, 2 * radius)

    # Setup brushes
    for center_x, center_y, in area:
        # How many entries in this brush depending on the position
        num_entries = 0
        # If the coordinates are in the area 
        if (center_y <= radius or center_y >= height - radius or center_x <= radius or center_x >= width - radius):
            weight_sum = 0
            for rad_x, rad_y in radius_area:
                # From -radius to +radius
                offset_x, offset_y = rad_x - radius, rad_y - radius
                sqr_dst = offset_x ** 2 + offset_y ** 2
                # Filter only circular values
                if (sqr_dst < radius * radius):
                    if area.valid(center_x + offset_x, center_y + offset_y):
                        # If coords are actually in the heightmap
                        weight = 1 - math.sqrt(sqr_dst) / radius
                        weight_sum += weight
                        weights_and_offsets[num_entries] = [
                            offset_x, offset_y, weight]
                        num_entries += 1
        # Init brush data
        erosion_brushes[center_y, center_y] = [
            None for i in range(num_entries)]

        # Initialize the brush
        for j in range(num_entries):
            erosion_brushes[center_y, center_x][j] = [
                center_x + weights_and_offsets[j][0],  # X coordinate
                center_y + weights_and_offsets[j][1],  # Y coordinate
                weights_and_offsets[j][2] / weight_sum  # Weight of the brush
            ]


class __HeightAndGradient():
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

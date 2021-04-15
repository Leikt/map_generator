#! /usr/bin/env python3
# coding: utf-8

import logging
import random
import math
import numpy

import opensimplex
from src.helpers.chrono import chrono


@chrono
def generate(parameters, width: int, height: int, seed: int) -> object:
    """Generate a island heightmap using the given parameters
    Parameters
    ==========
        width: int
    The heightmap width
        height: int
    The heightmap height
        seed: int
    The randomness seed
        octaves: int
    The number of octave in noise generation
        persistence: float
    The persistence of the noise
        lacunarity: float
    The lacunarity of the noise
        initial_scale: float
    The initial scale of the noise
        radius_coef: float
    The island radius coef applied to the map width or height depending what's smaller
        center_radius_coef: float
    The island minimum radius in x coordinates, coef applied to map  width or height depending what's smaller
        variation_initial_scale: float
    Radius variation noise initial scale
        variation_amplitude_coef: float
    Radius variation max amplitude, coef applied to width or height depending what's smaller
        ease_power: int
    Modify the steep overhal value
        **unused
    Other unused arguments, hack to use **large_hash when calling this method
    Returns
    =======
        numpy 2d array
    The result of the generation"""

    # Retrieve parameters
    try:
        octaves = parameters.octaves
        persistence = parameters.persistence
        lacunarity = parameters.lacunarity
        initial_scale = parameters.initial_scale
        radius_coef = parameters.radius_coef
        center_radius_coef = parameters.center_radius_coef
        variation_initial_scale = parameters.variation_initial_scale
        variation_amplitude_coef = parameters.variation_amplitude_coef
        ease_power = parameters.ease_power
    except AttributeError as e:
        logging.critical(
            "A required parameter is missing from the parameters : \n{err}".format(err=e))

    # Initialize working variables
    heightmap = numpy.zeros((width, height), numpy.float32)
    prng = random.Random(seed)
    get_noise = opensimplex.OpenSimplex(seed).noise2d
    offsets = list(map(lambda o: (prng.randint(-1000, 1000),
                   prng.randint(-1000, 1000)), [None] * octaves))
    scale_clamp = float(min(width, height))
    radius = radius_coef * scale_clamp / 2
    radius_center = center_radius_coef * scale_clamp / 2
    variation_amplitude = variation_amplitude_coef * scale_clamp / 2
    center_x = int(width / 2)
    center_y = int(height / 2)
    # Some optimization of function calling
    math_sqrt = math.sqrt
    math_asin = math.asin
    math_acos = math.acos
    radius_ease_power = radius ** ease_power

    # Generating each value
    for x in range(width):
        for y in range(height):
            # Center exclusion
            if x == center_x and y == center_y:
                continue
            # Init and calculate distance
            value = 0.0
            distance = math_sqrt(
                (center_x - x) * (center_x - x) + (center_y - y) * (center_y - y))
            if distance <= radius:
                # Calculate variation of the circle radius
                angle = math_asin((y - center_y) / distance) * \
                    math_acos((x - center_x) / distance)
                angle_noise = (get_noise(angle, 0) + 1) / 2
                variation = variation_amplitude * angle_noise
                if distance <= radius - variation:
                    # Emerged lands = calculate height
                    # Calculate ease coefficient
                    coef_ease = 1 - (distance ** ease_power) / \
                        radius_ease_power
                    # Radius variation coefficient
                    if distance <= radius_center:
                        coef_variation = 1
                    else:
                        coef_variation = 1 - \
                            (distance - radius_center) / \
                            (radius - variation - radius_center)
                    # Actual height calculation based on noise
                    scale = initial_scale
                    weight = 1.0
                    for ox, oy in offsets:
                        # Each octave have less impact than the previous
                        value += (get_noise(ox + scale * x / scale_clamp,
                                  oy + scale * y / scale_clamp) + 1) * weight
                        weight *= persistence
                        scale *= lacunarity
                    # Apply island ease to sea coefficients
                    value = value * coef_ease * coef_variation

            # Store height
            heightmap[x, y] = value

    # Set the center value to the average of 4 neightbour
    heightmap[center_x, center_y] = (heightmap[center_x, center_y - 1] +
                                     heightmap[center_x, center_y + 1] +
                                     heightmap[center_x - 1, center_y] +
                                     heightmap[center_x + 1, center_y]) / 4

    # Correcting data to put them between -1.0 and 1.0
    lowest = numpy.amin(heightmap)
    highest = numpy.amax(heightmap)
    if lowest != highest:
        delta = highest - lowest
        heightmap = numpy.array(
            list(map(lambda v: (v - lowest) / delta, heightmap)), numpy.float64)

    # Return the heightmap
    return heightmap

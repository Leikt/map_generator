#! /usr/bin/env python3
# coding: utf-8

import logging
import random
import math

import opensimplex
from src.helpers.chrono import chrono
from src.raw.heightmap import Heightmap


@chrono
def generate(*, width: int, height: int, seed: int, octaves: int,
             persistence: float, lacunarity: float, initial_scale: float,
             radius_coef: float, center_radius_coef: float, variation_initial_scale: float,
             variation_amplitude_coef: float, ease_power: float,
             **unused) -> Heightmap:
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
        HeightMap
    The result of the generation"""

    # Initialize working variables
    heightmap = Heightmap(width, height)
    prng = random.Random(seed)
    simplex = opensimplex.OpenSimplex(seed)
    offsets = [None] * octaves
    for i in range(octaves):
        offsets[i] = (prng.randint(-1000, 1000), prng.randint(-1000, 1000))
    scale_clamp = float(min(width, height))
    radius = radius_coef * scale_clamp / 2
    radius_center = center_radius_coef * scale_clamp / 2
    variation_amplitude = variation_amplitude_coef * scale_clamp / 2
    center_x = int(width / 2)
    center_y = int(height / 2)

    # Generating each value
    for x, y in heightmap.coordinates:
        # Center exclusion
        if x == center_x and y == center_y:
            continue
        # Init and calculate distance
        value = 0.0
        distance = math.sqrt((center_x - x) ** 2 + (center_y - y) ** 2)
        if distance <= radius:
            # Calculate variation
            angle = math.asin((y - center_y) / distance) * \
                math.acos((x - center_x) / distance)
            angle_noise = (simplex.noise2d(angle, 0) + 1) / 2
            variation = variation_amplitude * angle_noise
            if distance <= radius - variation:
                # Emerged lands = calculate height
                # Calculate ease coefficient
                coef_ease = 1 - distance ** ease_power / radius ** ease_power
                # Radius variation coefficient
                if distance <= radius_center:
                    # coef_variation = 1 - distance * \
                    #     (distance - radius_center) / \
                    #     (radius_center * (radius - variation - radius_center))
                    coef_variation = 1
                else:
                    coef_variation = 1 - \
                        (distance - radius_center) / \
                        (radius - variation - radius_center)
                # Actual height calculation based on noise
                scale = initial_scale
                weight = 1.0
                for i in range(octaves):
                    pX = offsets[i][0] + scale * x / scale_clamp
                    pY = offsets[i][0] + scale * y / scale_clamp
                    value += (simplex.noise2d(pX, pY) + 1) * weight
                    # Each octave have less impact than the previous
                    weight *= persistence
                    scale *= lacunarity
                # Apply island ease to sea coefficients
                value *= coef_ease * coef_variation

        # Store height
        heightmap[x, y] = value

    # Set the center value to the average of 4 neightbour
    heightmap[center_x, center_y] = (heightmap[center_x, center_y - 1] +
                                     heightmap[center_x, center_y + 1] +
                                     heightmap[center_x - 1, center_y] +
                                     heightmap[center_x + 1, center_y]) / 4

    # Correcting data to put them between -1.0 and 1.0
    minValue = heightmap.lowest
    maxValue = heightmap.highest
    if maxValue != minValue:
        for x, y in heightmap.coordinates:
            heightmap[x, y] = (heightmap[x, y] - minValue) / \
                (maxValue - minValue)

    # Return the heightmap
    return heightmap

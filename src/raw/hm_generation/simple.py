#! /usr/bin/env python3
# coding: utf-8

import logging
import random
import numpy

import opensimplex
from src.helpers.chrono import chrono


@chrono
def generate(parameters, width: int, height: int, seed: int) -> object: #, octaves: int, persistence: float, lacunarity: float, initial_scale: float, **unused) -> object:
    """Generate a simple heightmap using the given parameters
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
        **unused
    Other unused arguments, hack to use **large_hash when calling this method
    Returns
    =======
        numpy array
    The result of the generation"""

    # Retrieve parameters
    try:
        octaves = parameters.octaves
        persistence = parameters.persistence
        lacunarity = parameters.lacunarity
        initial_scale = parameters.initial_scale
    except AttributeError as e:
        logging.critical(
            "A required parameter is missing from the parameters : \n{err}".format(err=e))

    # Initialize working variables
    heightmap = numpy.zeros((width, height), numpy.float64)
    prng = random.Random(seed)
    get_noise = opensimplex.OpenSimplex(seed).noise2d
    offsets = list(map(lambda o: (prng.randint(-1000, 1000),
                   prng.randint(-1000, 1000)), [None] * octaves))
    scale_clamp = float(min(width, height))

    # Generating each value
    for x in range(width):
        for y in range(height):
            value = 0.0
            scale = initial_scale
            weight = 1.0
            for ox, oy in offsets:
                # Each octave have less impact than the previous
                value = value + (get_noise(ox + scale * x / scale_clamp, oy + scale * y / scale_clamp) + 1) * weight
                weight = weight * persistence
                scale = scale * lacunarity
            # Store height
            heightmap[x, y] = value

    # Correcting data to put them between -1.0 and 1.0
    lowest = numpy.amin(heightmap)
    highest = numpy.amax(heightmap)
    if lowest != highest:
        delta = highest - lowest
        heightmap = numpy.array(
            list(map(lambda v: (v - lowest) / delta, heightmap)), numpy.float64)

    # Return the heightmap
    return heightmap

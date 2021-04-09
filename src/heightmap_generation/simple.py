#! /usr/bin/env python3
# coding: utf-8

import logging
import random

import opensimplex
from src.chrono import chrono
from src.heightmap import Heightmap


@chrono
def generate(**kwargs) -> Heightmap:
    """Generate a simple heightmap using the given parameters"""

    # Retrieve parameters
    try:
        heightmap = Heightmap(kwargs["width"], kwargs["height"])
        seed = random.randint(0, 100_000_000_000) if kwargs.get(
            "randomizeSeed", False) else kwargs["seed"]
        octaves = kwargs["octaves"]
        persistence = kwargs["persistence"]
        lacunarity = kwargs["lacunarity"]
        initialScale = kwargs["scale"]
    except Exception as e:
        logging.critical(
            "Wrong or missing parameter in simple heightmap \
            generation.\nParameters:{params}\nError: \
            {msg}".format(params=kwargs, msg=e))

    # Initialize working variables
    prng = random.Random(seed)
    simplex = opensimplex.OpenSimplex(seed)
    offsets = [None] * octaves
    for i in range(octaves):
        offsets[i] = (prng.randint(-1000, 1000), prng.randint(-1000, 1000))
    minValue = -100_000_000_000
    maxValue = 100_000_000_000
    width = float(heightmap.width)
    height = float(heightmap.height)

    # Generating each value
    for x, y in heightmap.coordinates:
        value = 0.0
        scale = initialScale
        weight = 1.0
        for i in range(octaves):
            pX = offsets[i][0] + scale * x / width
            pY = offsets[i][0] + scale * y / height
            value += simplex.noise2d(pX, pY) * weight
            # Each octave have less impact than the previous
            weight *= persistence
            scale *= lacunarity
        heightmap[x, y] = value
        minValue = min(minValue, value)
        maxValue = max(maxValue, value)

    # Correcting data to put them between -1.0 and 1.0
    if maxValue != minValue:
        for x, y in heightmap.coordinates:
            heightmap[x, y] = (heightmap[x, y] - minValue) / (maxValue - minValue)
    
    # Return the heightmap
    return heightmap

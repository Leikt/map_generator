#! /usr/bin/env python3
# coding: utf-8

import logging
import random

import opensimplex
from src.helpers.chrono import chrono
from src.raw.heightmap import Heightmap


@chrono
def generate(*, width: int, height: int, seed: int, octaves: int, persistence: float, lacunarity: float, initial_scale: float, **unused) -> Heightmap:
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

    # Generating each value
    for x, y in heightmap.coordinates:
        value = 0.0
        scale = initial_scale
        weight = 1.0
        for i in range(octaves):
            pX = offsets[i][0] + scale * x / scale_clamp
            pY = offsets[i][0] + scale * y / scale_clamp
            value += simplex.noise2d(pX, pY) * weight
            # Each octave have less impact than the previous
            weight *= persistence
            scale *= lacunarity
        # Store height
        heightmap[x, y] = value

    # Correcting data to put them between -1.0 and 1.0
    minValue = heightmap.lowest
    maxValue = heightmap.highest
    if maxValue != minValue:
        for x, y in heightmap.coordinates:
            heightmap[x, y] = (heightmap[x, y] - minValue) / \
                (maxValue - minValue)

    # Return the heightmap
    return heightmap

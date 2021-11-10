#! /usr/bin/env python3
# coding: utf-8

import logging
import random
import numpy as np

from src.helpers.chrono import chrono


@chrono
def generate(parameters: object, width: int, height: int, seed: int) -> object:
    heightmap = np.zeros((width, height), np.float32)
    for x in range(width):
        for y in range(height):
            if y < 0.1 * height:
                heightmap[x, y] = 1
            elif y > 0.9 * height:
                heightmap[x, y] = 0
            else:
                heightmap[x, y] = 1 - (y - 0.1 * height) / (0.9 * height - 0.1 * height)
    return heightmap
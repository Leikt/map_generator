#! /usr/bin/env python3
# coding: utf-8

import logging
import random

from src.helpers.chrono import chrono
from src.raw.heightmap import Heightmap


@chrono
def generate(*, width: int, height: int, **unused) -> Heightmap:
    heightmap = Heightmap(width, height)
    for x, y in heightmap.coordinates:
        if y < 0.1 * height:
            heightmap[y, x] = 1
        elif y > 0.9 * height:
            heightmap[y, x] = 0
        else:
            heightmap[y, x] = 1 - (y - 0.1 * height) / (0.9 * height - 0.1 * height)
    return heightmap
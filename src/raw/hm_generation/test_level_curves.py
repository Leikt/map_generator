#! /usr/bin/env python3
# coding: utf-8

import logging
import random
import numpy as np

from src.helpers.chrono import chrono

DATA = [
    [3,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,3,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,4],
]

@chrono
def generate(parameters: object, width: int, height: int, seed: int) -> object:
    heightmap = np.array(DATA)
    return heightmap
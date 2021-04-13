#! /usr/bin/env python3
# coding: utf-8

import importlib
import logging

from src.raw.rawmap import RawMap
import src.raw.erosion as erosion

"""Manage the rawmap generation process"""


def generate(parameters: hash) -> RawMap:
    """Generate a raw map using the given parameters
    Parameters
    ==========
        parameters: hash
    hash containing the parameters of the generation
    Returns
    =======
        RawMap
    The result of the generation
    Raises
    ======
        ValueError
    If a parameters is missing or invalid"""

    # Retrieve parameters
    try:
        mapParams = parameters["map"]
        width = mapParams["width"]
        height = mapParams["height"]
        seed = parameters["seed"]
        hmgen_parameters = parameters["heightmap_generation"]
        hmgen_module_name = hmgen_parameters["type"]
        erosion_parameters = parameters["erosion"]
        del mapParams  # Useless variable
    except KeyError as e:
        logging.critical(
            "A required parameter is missing from the parameters : \n{err}".format(err=e))

    # Retrieve the heightmap generation module
    try:
        hmgen_module_name = __package__ + ".hm_generation." + hmgen_module_name
        hmgen_module = importlib.import_module(hmgen_module_name)
    except ImportError as e:
        logging.critical("Impossible to load the heightmap generation module named : '{mod}'\n{err}".format(
            mod=hmgen_module_name, err=e))

    # Initialize rawmap
    rawmap = RawMap(width, height)

    # Generate the heightmap
    rawmap.heightmap = hmgen_module.generate(
        width=width, height=height, seed=seed, **hmgen_parameters)

    # Erode the heightmap
    erosion.erode(rawmap.heightmap, seed=seed, width=width,
                  height=height, **erosion_parameters)

    # Posterize heigtmap

    # Cliff mapping

    # Water mapping

    return rawmap

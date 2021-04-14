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
        map_params = parameters["map"]
        width = map_params["width"]
        height = map_params["height"]
        seed = parameters["seed"]
        hmgen_parameters = parameters["heightmap_generation"]
        hmgen_module_name = hmgen_parameters["type"]
        erosion_parameters = parameters["erosion"]
        del map_params  # Useless variable
    except KeyError as e:
        logging.critical(
            "A required parameter is missing from the parameters : \n{err}".format(err=e))

    # Load debug parameters
    try:
        debug_params = parameters["_debug"]
        debug_enabled = debug_params["enabled"]
        debug_step = debug_params["step"]
        debug_gen_id = debug_params["gen_id"]
        del debug_params
    except:
        debug_enabled = False

    # Retrieve the heightmap generation module
    try:
        hmgen_module_name = __package__ + ".hm_generation." + hmgen_module_name
        hmgen_module = importlib.import_module(hmgen_module_name)
    except ImportError as e:
        logging.critical("Impossible to load the heightmap generation module named : '{mod}'\n{err}".format(
            mod=hmgen_module_name, err=e))

    # Initialize debug
    if debug_enabled:
        from src.raw.steps import RawGenerationSteps
        if debug_gen_id is None:
            path, exists = RawGenerationSteps.default_path(parameters["_gen_id"])
        else:
            path, exists = RawGenerationSteps.default_path(debug_gen_id)
        gen_steps = RawGenerationSteps(path)
        gen_steps.setup()
        if not exists:
            debug_step = -1
    else:
        debug_step = -1

    # Initialize rawmap
    rawmap = None
    if debug_enabled:
        rawmap = RawMap.from_array(gen_steps.get_step(debug_step))
    if rawmap is None:
        rawmap = RawMap(width, height)
        debug_step = -1

    # Generate the heightmap
    if debug_step < 1: # Raw noise generation
        rawmap.heightmap = hmgen_module.generate(
            width=width, height=height, seed=seed, **hmgen_parameters)
        if debug_enabled:
            gen_steps.add_step(rawmap.to_array())

    # Erode the heightmap
    if debug_step < 2: # Erosion
        erosion.erode(rawmap.heightmap, seed=seed, width=width,
                  height=height, **erosion_parameters)
        if debug_enabled:
            gen_steps.add_step(rawmap.to_array())

    # Posterize heigtmap

    # Cliff mapping

    # Water mapping

    # Save debug bin
    if debug_enabled:
        gen_steps.save()

    return rawmap

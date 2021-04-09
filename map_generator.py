#! /usr/bin/env python3
# coding: utf-8

import importlib
import json
import logging

logging.basicConfig(level=logging.DEBUG)


def load_parameters(filename: str) -> hash:
    """Load the parameters from the file
    Parameters
    ==========
        filename: str
    The path to the parameters file
    Returns
    =======
        hash
    The parameters hash"""

    try:
        with open(filename) as file:
            return json.load(file)
    except FileNotFoundError as e:
        logging.critical("Can't find parameters file : {msg}".format(msg=e))
    except json.JSONDecodeError as e:
        logging.critical(
            "Error while decoding parameters file : {msg}".format(msg=e))
    except:
        logging.critical("Something went wrong while loading parameters.")


def load_heightmap_generation(module: str):
    """Load the heightmap generation function from matching the name
    Parameters
    ==========
        module: str
    The name of the generator, it can be 'simple', 'island', 'volcano', 'flat'...
    Returns
    =======
        lambda(**kwargs) -> Heightmap
    The function to call to generate heightmap
    Raise
    =====
        ImportError
    If the given name doesn't match any module"""

    try:
        return importlib.import_module(
            "src.heightmap_generation.{mod}".format(mod=module))
    except ImportError as e:
        logging.critical(
            "Can't find the heightmap generation module named '{mod}'. Raise the error : {err}".format(mod=module, err=e))


def run():
    """Run the generation"""
    # Load the parameters
    parameters = load_parameters("generation_parameters.json")
    
    # Generate the heightmap
    hm_generation = load_heightmap_generation(
        parameters["heightmapGeneration"]["module"])
    hm = hm_generation.generate(**parameters["heightmapGeneration"], **parameters["map"],
                                seed=parameters["seed"], randomizeSeed=parameters["randomizeSeed"])
    # Erode the heightmap
    # TODO
    # Posterize the heightmap
    # TODO
    # Create cliffmap
    # TODO
    # Place life water
    # TODO
    # Place biomes
    # TODO

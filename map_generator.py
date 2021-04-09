#! /usr/bin/env python3
# coding: utf-8

import json
import logging

from src.heightmap_generation import simple as hm_generation

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


def run():
    """Run the generation"""
    parameters = load_parameters("generation_parameters.json")
    hm = hm_generation.generate(**parameters["heightmapGenerator"], **parameters["map"],
                                seed=parameters["seed"], randomizeSeed=parameters["randomizeSeed"])

#! /usr/bin/env python3
# coding: utf-8

import json
import logging
import random
import os
import time

import src.exporters.png as exporter_png
import src.raw.rawmap_generation as rawmap_generation

"""Manage the entire generation process"""


def run(path_to_params: str):
    """Process a full generation
    Parameters
    ==========
        path_to_params: str
    Absolute path to the parameters json file
    Raises
    ======
        Exception
    If there is a problem with the file"""

    # Retrieve parameters
    parameters = __load_parameters(path_to_params)
    if parameters is None:
        raise Exception(
            "No parameters found. Error with the file '{f}'".format(f=path_to_params))

    # Randomize the main seed if asked
    parameters["seed"] = random.randint(0, 2 ** 64 - 1) if parameters.get(
        "randomize_seed", False) else parameters["seed"]

    # Generate the raw map
    rawmap = rawmap_generation.generate(parameters)

    # Generate the tilemap
    # TODO

    # Exports
    # Generate path to outputs
    gen_id = str(round(time.time()))
    dir_outputs = __gen_path_to_outputs(gen_id, parameters["outputs"])

    # Export heightmap
    path_to_rawmap_png = os.path.join(dir_outputs, "rawmap.png")
    hm_npy = rawmap.heightmap.to_numpy()
    exporter_png.export(path_to_rawmap_png, rawmap.width,
                        rawmap.height, hm_npy)


def __load_parameters(path_to_param: str) -> hash:
    try:
        with open(path_to_param) as file:
            return json.load(file)
    except FileNotFoundError as e:
        logging.critical("Can't find parameters file : {msg}".format(msg=e))
    except json.JSONDecodeError as e:
        logging.critical(
            "Error while decoding parameters file : {msg}".format(msg=e))
    except:
        logging.critical("Something went wrong while loading parameters.")
    # Code reached when the file couldn't be loaded
    return None

def __gen_path_to_outputs(gen_id: str, param_output: str):
    dirname = os.path.dirname(os.path.dirname(__file__))
    path_to_outputs = param_output.format(
        directory=dirname, id=gen_id)
    if not os.path.exists(path_to_outputs):
        os.mkdir(path_to_outputs)
    return path_to_outputs
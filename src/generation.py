#! /usr/bin/env python3
# coding: utf-8

import json
import logging

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

    # Generate the raw map
    try:
        rawmap = rawmap_generation.generate(parameters)
    except ValueError as e:
        logging.critical(
            "Error while generating the rawmap : \n{err}".format(err=e))

    # Generate the tilemap
    # try:
    #     tilemap = tilemap_generation.generate(parameters)
    # except ValueError as e:
    #     logging.critical(
    #         "Error while generating the tilemap : \n{err}".format(err=e))


    # Export


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

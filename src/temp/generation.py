"""Module to call to launche generation from parameters"""

import os
import logging
import json

def load_parameters(path: str) -> hash:
    """Load the parameters from the file
    Parameters
    ==========
        path: str
    The path to the parameters file
    Returns
    =======
        hash
    The parameters hash"""

    try:
        with open(path) as file:
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

def run(param_filename: str):
    # Retrieve parameters
    dirname = os.path.dirname(os.path.dirname(__file__))
    path_to_params = os.path.join(dirname, param_filename)
    parameters = load_parameters(path_to_params)
    
    # Configure debug
    debug = parameters["debug"]
    debug_enabled = debug.get("enabled", False) if debug is not None else False
    load_enabled = debug.get("loadEnabled", False) if debug is not None and debug_enabled else False

    # Run the generation with the options
    if load_enabled and debug["loadBase"]:
        # Load the base heightmap
        # standard_loading
        pass
    else:
        # Generate the heightmap
        # actual_logic
        # Save the heightmap
        # standard_export
        pass
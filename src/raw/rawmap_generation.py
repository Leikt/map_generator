#! /usr/bin/env python3
# coding: utf-8

import importlib
import logging
import os

from src.raw.rawmap import RawMap
from src.raw.level_curves import LevelCurves
from src.raw.erosion import Erosion
from src.generation_step_manager import GenerationStepManager
import collections


class RawMapGeneration():
    """Generate a RawMap object
    Parameters
    ==========
        parameters: object
    A SimpleNamespace object with attributes (sea Parameters.parameters)
        path_to_outputs: str
    Path to the output folder where the 'rawmap_steps.bin' file will be stored
        debug_enabled: bool
    True if the debug is enabled, needs to be false in the releases
        debug_step: int
    The step where to begin the rawmap generation
    Parameters.parameters
    =====================
    What attribute the parameters argument needs to have
        seed: int
    Generation randomness seed
        map
    Another object with the width and height arguments
        heightmap_generation
    Another object with heightmap generation, specific to each generation types
        erosion
    Another object with erosion parameters, specific to the erosion module"""

    STEPS = collections.namedtuple('Steps',\
        ['heightmap', 'erosion', 'cliff_mapping', 'water_mapping'])\
        (1, 2, 3, 4)

    def __init__(self, parameters: object, path_to_outputs: str, debug_enabled: bool, debug_step: int):
        # Setup attributes
        self._parameters = parameters
        self._path_to_outputs = path_to_outputs

        # Init the step manager and the generated data
        path_to_steps = os.path.join(self._path_to_outputs, "rawmap_steps.bin")
        self._step_manager = GenerationStepManager(
            debug_enabled, path_to_steps, debug_step, RawMap)
        self._step_manager.load()
        self._step_manager.init_data(
            self._parameters.map.width, self._parameters.map.height)

        # Generate
        self.generate()

        # Save the steps
        self._step_manager.save()

    @property
    def rawmap(self):
        """Access the rawmap property"""
        return self._step_manager.data

    def generate(self):
        """Generate the raw map"""

        # Generate raw heightmap
        self._generate_heightmap()

        # Erode the heightmap
        self._erode()

        # Cliff mapping
        self._cliff_mapping()

        # Water mapping

    def _generate_heightmap(self):
        # Retrieve parameters
        try:
            seed = self._parameters.seed
            hmgen_parameters = self._parameters.heightmap_generation
            hmgen_module_name = self._parameters.heightmap_generation.type
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))

        # Retrieve the heightmap generation module
        try:
            hmgen_module_name = __package__ + ".hm_generation." + hmgen_module_name
            hmgen_module = importlib.import_module(hmgen_module_name)
        except ImportError as e:
            logging.critical("Impossible to load the heightmap generation module named : '{mod}'\n{err}".format(
                mod=hmgen_module_name, err=e))

        # Actually generate the heightmap
        @self._step_manager.make_step(self.STEPS.heightmap)
        def heightmap():
            self.rawmap.heightmap = hmgen_module.generate(
                hmgen_parameters, self.rawmap.width, self.rawmap.height, seed)
            return self.rawmap
        heightmap()

    def _erode(self):
        # Retrieve erosion parameters
        try:
            seed = self._parameters.seed
            erosion_parameters = self._parameters.erosion
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))

        # Erode the heightmap
        @self._step_manager.make_step(self.STEPS.erosion)
        def erode():
            erosion = Erosion(erosion_parameters, self.rawmap.heightmap,
                              self.rawmap.width, self.rawmap.height, seed)
            erosion.init_brushes()
            erosion.erode()
            return self.rawmap
        erode()

    def _cliff_mapping(self):
        # Retrieve cliff mapping parameters
        try:
            cliff_mapping_parameters = self._parameters.cliff_mapping
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))

        # Create the cliff map
        @self._step_manager.make_step(self.STEPS.cliff_mapping)
        def cliff_map():
            level_curves = LevelCurves(cliff_mapping_parameters, self.rawmap.heightmap, self.rawmap.width, self.rawmap.height)
            level_curves.create_level_curves()
            self.rawmap.level_curves = level_curves.result
            return self.rawmap
        cliff_map()
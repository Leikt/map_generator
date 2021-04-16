#! /usr/bin/env python3
# coding: utf-8

import collections
import importlib
import logging
import os

from src.generation_step_manager import GenerationStepManager
from src.helpers.chrono import chrono
from src.raw.erosion import Erosion
from src.raw.stratums import Stratums
from src.raw.cliffs import Cliffs
from src.raw.rawmap import RawMap


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
        ['heightmap', 'erosion', 'stratums', 'cliffs', 'water_mapping'])\
        (1, 2, 3, 4, 5)

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

    @chrono
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

        # Create the stratums
        @self._step_manager.make_step(self.STEPS.stratums)
        def create_stratums():
            stratums = Stratums(cliff_mapping_parameters, self.rawmap.heightmap, self.rawmap.width, self.rawmap.height)
            stratums.calculate_stratums()
            self.rawmap.stratums = stratums.stratums
            return self.rawmap
        create_stratums()

        # Create the cliffs
        @self._step_manager.make_step(self.STEPS.cliffs)
        def create_cliffs():
            cliffs_gen = Cliffs(cliff_mapping_parameters, self.rawmap.stratums, self.rawmap.width, self.rawmap.height)
            cliffs_gen.calculate_cliffs()
            self.rawmap.cliffs = cliffs_gen.cliffs
            self.rawmap.rgb_cliffs = cliffs_gen.to_rgb_cliff(cliffs_gen.cliffs, self.rawmap.width, self.rawmap.height)
            return self.rawmap
        create_cliffs()

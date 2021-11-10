#! /usr/bin/env python3
# coding: utf-8

import collections
import importlib
import logging
import os

import numpy
from src.generation_step_manager import GenerationStepManager
from src.helpers.chrono import chrono
from src.helpers.resize import resize_data
from src.raw.cliffs import Cliffs
from src.raw.erosion import Erosion
from src.raw.rawmap import RawMap
from src.raw.stratums import Stratums
from src.raw.waterfalls import Waterfalls
from src.raw.waters import Waters


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
    Another object with erosion parameters, specific to the erosion module
        cliff_mapping
    Another object with cliff mapping parmaters, specific to the cliff mapping module"""

    STEPS = collections.namedtuple('Steps',
                                   ['heightmap', 'erosion', 'stratums', 'cliffs', 'waters', 'resizing', 'waterfalls'])(1, 2, 3, 4, 5, 6, 7)

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
        self._water_mapping()

        # Resize to its final form
        self._resize()

        # Map the waterfalls
        self._waterfalls()

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
                hmgen_parameters, self.rawmap.working_width, self.rawmap.working_height, seed)
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
                              self.rawmap.working_width, self.rawmap.working_height, seed)
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
            stratums = Stratums(cliff_mapping_parameters, self.rawmap.heightmap,
                                self.rawmap.working_width, self.rawmap.working_height)
            stratums.calculate_stratums()
            self.rawmap.stratums = stratums.stratums
            return self.rawmap
        create_stratums()

        # Create the cliffs
        @self._step_manager.make_step(self.STEPS.cliffs)
        def create_cliffs():
            cliffs_gen = Cliffs(cliff_mapping_parameters, self.rawmap.stratums,
                                self.rawmap.working_width, self.rawmap.working_height)
            cliffs_gen.calculate_cliffs()
            self.rawmap.cliffs = cliffs_gen.cliffs
            return self.rawmap
        create_cliffs()

    def _water_mapping(self):
        # Retrieve water mapping parameters
        try:
            seed = self._parameters.seed
            water_mapping_parameters = self._parameters.water_mapping
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))

        # Generate the water map
        @self._step_manager.make_step(self.STEPS.waters)
        def create_waters():
            waters_gen = Waters(water_mapping_parameters, self.rawmap,
                                self.rawmap.working_width, self.rawmap.working_height, seed)
            waters_gen.generate()
            self.rawmap.rivermap = waters_gen.rivermap
            self.rawmap.poolmap = waters_gen.poolmap
            return self.rawmap
        create_waters()

    def _resize(self):
        # Retrieve cliff mapping parameters
        try:
            cliff_mapping_parameters = self._parameters.cliff_mapping
        except AttributeError as e:
            logging.critical(
                "A required parameter is missing from the parameters : \n{err}".format(err=e))

        # Resize the stratums to get rid of the orphans
        @self._step_manager.make_step(self.STEPS.resizing)
        @chrono
        def resizing():
            w_width, w_height = self.rawmap.working_width, self.rawmap.working_height
            self.rawmap.stratums, _w, _h = resize_data(
                self.rawmap.stratums, w_width, w_height, 2)

            # Recalculate the cliffs the cliff map
            cliffs_gen = Cliffs(cliff_mapping_parameters, self.rawmap.stratums,
                                self.rawmap.final_width, self.rawmap.final_height)
            cliffs_gen.calculate_cliffs()
            self.rawmap.cliffs = cliffs_gen.cliffs

            # Resize the rivers and pool maps
            self.rawmap.rivermap, _w, _h = resize_data(
                self.rawmap.rivermap, w_width, w_height, 2)
            self.rawmap.poolmap, _w, _h = resize_data(
                self.rawmap.poolmap, w_width, w_height, 2)
            return self.rawmap
        resizing()

    def _waterfalls(self):
        # Detect the waterfall
        @self._step_manager.make_step(self.STEPS.waterfalls)
        def create_waterfalls():
            waterfall_gen = Waterfalls(
                self.rawmap, self.rawmap.final_width, self.rawmap.final_height)
            waterfall_gen.calculate_waterfalls()
            self.rawmap.waterfallmap = waterfall_gen.waterfalls
            return self.rawmap
        create_waterfalls()

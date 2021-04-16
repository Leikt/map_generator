#! /usr/bin/env python3
# coding: utf-8

import json
import logging
import os
import random
import time
from types import SimpleNamespace

from src.helpers.chrono import chrono

from src.raw.rawmap import RawMap
import src.exporters.png as exporter_png
from src.raw.rawmap_generation import RawMapGeneration
from src.generation_step_manager import GenerationStepManager

class Generation():
    SEED_RANGE = (0, 2 ** 32 - 1)

    def __init__(self, parameters: object):
        # Retrieve the parameters
        self._parameters = self._load_parameters(parameters)
        self._debug_enabled = hasattr(
            self._parameters, '_debug') and self._parameters._debug.enabled
        self._debug_step = self._parameters._debug.step if self._debug_enabled else -1
        # Run the generation
        self.run()

    @chrono
    def run(self):
        # Randomize the seed if required
        if self._parameters.randomize_seed:
            self.seed = random.randint(*self.SEED_RANGE)

        # Init export folders
        path = self._get_path()
        if not os.path.exists(path):
            os.mkdir(path)

        # Generate Rawmap
        rawmap = RawMapGeneration(self._parameters, path, self._debug_enabled, self._debug_step).rawmap
        exporter_png.export(os.path.join(path, "heightmap.png"), rawmap.width, rawmap.height, rawmap.heightmap)
        exporter_png.export(os.path.join(path, "statums.png"), rawmap.width, rawmap.height, rawmap.stratums)
        exporter_png.export(os.path.join(path, "cliffs.png"), rawmap.width, rawmap.height, rawmap.cliffs)

        # Generate Tilemap

        # Export

    def _get_path(self) -> str:
        """Create the path to the export folder
        Returns
        =======
            str
        The path"""

        # Main directory
        dirname = os.path.dirname(os.path.dirname(__file__))
        # The generation id and folder name : use debug if it's enabled else generate new unique one
        self.gen_id = self._parameters._debug.name if self._debug_enabled else str(
            round(time.time()))
        # Return the formated path
        return self._parameters.outputs.format(
            directory=dirname, folder=self.gen_id)

    def _load_parameters(self, path_to_params: str) -> object:
        """Load the parameters from the file to a hash
        Parameters
        ==========
            path_to_params: str
        Path to the parameters file
        Returns
        =======
            object or None
        A object if the file could be loaded, None if not"""

        try:
            with open(path_to_params) as file:
                return json.load(file, object_hook=lambda d: SimpleNamespace(**d))
        except FileNotFoundError as e:
            logging.critical(
                "Can't find parameters file : {msg}".format(msg=e))
        except json.JSONDecodeError as e:
            logging.critical(
                "Error while decoding parameters file : {msg}".format(msg=e))
        except Exception as e:
            logging.critical(
                "Something went wrong while loading parameters:\n{msg}".format(msg=e))
        # Code reached when the file couldn't be loaded
        return None

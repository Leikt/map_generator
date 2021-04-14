#! /usr/bin/env python3
# coding: utf-8

from src.loaders import binary
import os



    # "_debug":{
    #     "enabled":false,
    #     "gen_id":null,
    #     "step":0
    # },

class RawGenerationSteps():
    def __init__(self, path: str):
        self._path = path
    
    def setup(self):
        try:
            self._data = binary.load(self._path)
        except:
            self._data = []

    def get_step(self, step: int) -> object:
        if step < 0 or step >= len(self._data):
            return None
        else:
            return self._data[step]

    def add_step(self, step: object):
        self._data.append(step)
    
    def save(self):
        binary.export(self._path, self._data)

    @staticmethod
    def default_path(gen_id: str):
        dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(dirname, "outputs", gen_id, "step.bin")
        return path, os.path.exists(path)

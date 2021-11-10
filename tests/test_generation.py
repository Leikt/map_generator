#! /usr/bin/env python3
# coding: utf-8

import unittest
import os
from src.generation import Generation

class Test_Generation(unittest.TestCase):
    def test_creation(self):
        # Create the path
        path = os.path.dirname(__file__)
        path = os.path.join(path, "generation_test_parameters.json")

        # Generate
        g = Generation(path)
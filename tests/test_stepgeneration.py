#! /usr/bin/env python3
# coding: utf-8

import unittest
import os

from src.generation_step_manager import GenerationStepManager

class Foo():
    def __init__(self, message):
        self.message = message

    def display(self):
        print(self.message)

    def to_array(self):
        return [self.message]

    @staticmethod
    def from_array(arr):
        return Foo(arr[0])


class Test_GenerationStepManager(unittest.TestCase):
    def test_general_logic(self):
        # Initialize
        #                       enabled,                path,             step, data_class
        path = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(path, "tests", "outputs")
        path_to_file = os.path.join(path, "step1.bin")
        # Delete previous outputs
        if os.path.exists(path_to_file):
            os.remove(path_to_file)
        # Test path
        fg = GenerationStepManager(True, path_to_file, -1, Foo)
        self.assertEqual(fg.path, path_to_file)
        # Test initialization
        data = fg.init_data("STEP_0")
        self.assertIsNotNone(data)
        self.assertIsInstance(data, Foo)

        # Generation
        @fg.make_step(1)
        def step_1():
            data.message += ",STEP_1"
            return data
        @fg.make_step(3)
        def step_3():
            data.message += ",STEP_3"
            return data
        step_1()
        step_3()
        # Test data
        self.assertEqual(data.message, "STEP_0,STEP_1,STEP_3")
        # Test save
        self.assertFalse(os.path.exists(path_to_file))
        fg.save()
        self.assertTrue(os.path.exists(path_to_file))
        
        del fg, data

        # Test loading
        fg = GenerationStepManager(True, path_to_file, 1, Foo)
        fg.load()
        self.assertTrue(fg.loaded)
        data = fg.init_data("DUMMY")
        self.assertIsNotNone(data)
        self.assertNotEqual(data.message, "DUMMY")

        # Test a decorator step <= fg.step
        @fg.make_step(1)
        def do_nothing():
            data.message += ",NEW_STEP_1"
            return data
        do_nothing()
        self.assertEqual(data.message, "STEP_0,STEP_1")
        # Test a decorator step > fg.step
        @fg.make_step(3)
        def do_something():
            data.message = "".join([data.message, ",NEW_STEP_3"])
            return data
        do_something()
        self.assertEqual(data.message, "STEP_0,STEP_1,NEW_STEP_3")
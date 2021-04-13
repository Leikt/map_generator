#! /usr/bin/env python3
# coding: utf-8

import unittest
import numpy
from src.loaders import binary

class Test_Binary(unittest.TestCase):
    TEST_DATA = ["something", "is", "going", ['w', 'e', 'l', 'l'], [1, 2, 3, 4]]

    def test_binary_export(self):
        # Non bytes-like object
        class Dummy():
            pass
        # Check raises
        self.assertRaises(FileNotFoundError, binary.export, "this/file/does/not/exist.bin", Dummy())
        self.assertRaises(AttributeError, binary.export, "tests/outputs/bin_file.bin", Dummy())
        # Check saving
        data = self.TEST_DATA
        binary.export("tests/outputs/bin_file.bin", data)
        # Check loading
        data = binary.load("tests/outputs/bin_file.bin")
        self.assertEqual(data, self.TEST_DATA)
        # Check raises
        self.assertRaises(FileNotFoundError, binary.load, "this/file/does/not/exist.bin")

    def test_numpy(self):
        np_arr = numpy.zeros((100, 10))
        np_arr[12, 3] = 102
        binary.export("tests/outputs/bin_array.bin", np_arr)
        np_arr_loaded = binary.load("tests/outputs/bin_array.bin")
        self.assertEqual(np_arr_loaded[12, 3], 102)
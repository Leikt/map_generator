#! /usr/bin/env python3
# coding: utf-8

import pickle
import logging


def export(path: str, data: bytes):
    """Save the given data into the file
    Parameters
    ==========
        path: str
    Path to the bin file
        data: object
    Object that can be stored as binary
    Raises
    ======
        FileNorFoundError
    If the path leads to a non existing directory
        AttributeError
    If the data are not bytes-like"""

    with open(path, 'wb') as file:
        pickle.dump(data, file)

def load(path: str):
    """Load the bin file and return its content
    Parameters
    ==========
        path: str
    Path to the bin file
    Returns
    =======
        bytes-like
    The data in the file
    Raises
    ======
        FileNotFoundError
    If the file doesn't exists
    Warnings
    ========
        EOFError
    If the file is empty, it will return None"""
    
    with open(path, 'rb') as file:
        return pickle.load(file)
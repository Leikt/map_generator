#! /usr/bin/env python3
# coding: utf-8

from src.heightmap import Heightmap


class RawMap:
    def __init__(self, width, height):
        self._heightmap = Heightmap(width, height)

    @property
    def width(self):
        """Access the width property"""
        return self._heightmap.width

    @property
    def height(self):
        """Access the height property"""
        return self._heightmap.height

    @property
    def coordinates(self):
        """Access the coordinates property"""
        return self._heightmap.coordinates

    @property
    def heightmap(self):
        """Access the heightmap property"""
        return self._heightmap

    @heightmap.setter
    def heightmap(self, value):
        """Set the heightmap property"""
        self._heightmap = value

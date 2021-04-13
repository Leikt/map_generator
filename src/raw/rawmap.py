#! /usr/bin/env python3
# coding: utf-8

class RawMap:
    """Class that contains raw map data"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.heightmap = None

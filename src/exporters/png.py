#! /usr/bin/env python3
# coding: utf-8

import logging
import time

import numpy
from PIL import Image


def export(out: str, width: int, height: int, data: list):
    """Render the data into a png file
    Parameters
    ==========
        out: str
    Path to the out file
        width: int
    Width of the final image
        height: int
    Height of the final image
        data: list
    2d or 3d array containing the data. Id 2d, out will be B&W, else, it will be RGB
    Raises
    ======
        ValueError
    If the data dimenison are not 2 or 3"""

    # Create the rgb data
    rgb = numpy.zeros((width, height, 3), numpy.uint8)
    # Convert data to rgb data
    if data.ndim == 2:  # B&W
        rgb = __convert2DArray(data, width, height)
    elif data.ndim == 3:  # RGB
        rgb = __convert3DArray(data, width, height)
    else:
        raise ValueError(
            "Data must be 2 or 3 dimensionnal numpy array, it is {dim}.".format(dim=data.ndim))
    # Save the image
    image = Image.fromarray(rgb, 'RGB')
    image.save(out)


def exportRaw(out: str, data: list, rotate: bool = True):
    """Render the data as they comes
    Parameters
    ==========
        out: str
    Path to the out file
        data: list
    2d array of [R,G,B] elements"""
    
    # By default, the imagme will be renderer 90° right
    if rotate:
        width = len(data)
        height = len(data[0])
        rgb = numpy.zeros((height, width, 3), numpy.uint8)
        for x in range(width):
            for y in range(height):
                rgb[y, x] = data[x, y]
        data = rgb

    try:
        image = Image.fromarray(data, 'RGB')
        image.save(out)
    except Exception as e:
        logging.critical(
            "Something went wrong with theses data, please check them. Error : {err}".format(err=e))


def __convert2DArray(data, width, height):
    # Clamp data between 0 and 255
    # Calculate the currest lowest and highest
    minValue = numpy.amin(data)
    maxValue = numpy.amax(data)
    # Calculate the coefficient to convert current range into the wanted range
    coef = 1
    if(minValue != maxValue):
        coef = 255.0 / (maxValue - minValue)
    # Convert data into rgb data
    rgb = numpy.zeros((height, width, 3), numpy.uint8)
    for x in range(width):
        for y in range(height):
            value = int((data[x, y] - minValue) * coef)
            rgb[y, x] = [value, value, value]
    return rgb


def __convert3DArray(data, width, height):
    # Clamp data between 0 and 255
    # Calculate the currest lowest and highest
    minValue = numpy.amin(data)
    maxValue = numpy.amax(data)
    # Calculate the coefficient to convert current range into the wanted range
    coef = 1
    if(minValue != maxValue):
        coef = 255 / (maxValue - minValue)
    # Convert data into rgb data
    rgb = numpy.zeros((height, width, 3), numpy.uint8)
    for x in range(width):
        for y in range(height):
            r = data[x, y, 0] * coef
            g = data[x, y, 1] * coef
            b = data[x, y, 2] * coef
            rgb[y, x] = [r, g, b]
    return rgb

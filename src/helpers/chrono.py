#! /usr/bin/env python3
# coding: utf-8

import datetime
import logging
import timeit

def chrono(func):
    """Notify the duration of the decorated function execution"""
    def inner(*args, **kwargs):
        name = "".join([func.__module__,".",func.__name__])
        start = datetime.datetime.now()
        logging.debug("'{name}' started...".format(name=name))
        result = func(*args, **kwargs)
        logging.debug("'{name}' finished ({duration}s)".format(name=name, duration=datetime.datetime.now() - start))
        return result
    return inner
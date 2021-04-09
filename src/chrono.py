import datetime
import logging

def chrono(func):
    """Notify the duration of the decorated function execution"""
    def inner(*args, **kwargs):
        start = datetime.datetime.now()
        logging.debug("Execution of {name}...".format(name=func.__name__))
        result = func(*args, **kwargs)
        logging.debug("Finished after {duration}s".format(duration=datetime.datetime.now() - start))
        return result
    return inner
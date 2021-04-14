#! /usr/bin/env python3
# coding: utf-8

import os
import pickle


class GenerationStepManager():
    """Class that manage the loading and saving of the different generation steps. It's used to skip long process.
    
    Parameters
    ==========
        enabled: bool
    Indicate if the steps must be loaded or not
        dirname: str
    Directory where to save the steps.bin file
        step: int
    Id of the step, must be greater or equal to zero
        data_type: type
    Any type that has a to_array() method and a from_array(arr) static method"""

    def __init__(self, enabled: bool, path: str, step: int, data_type: type):
        self._enabled = enabled
        self._path = path
        self._data_type = data_type
        self._data = None
        self._step = step
        self._steps = {}
        self._loaded = False
        # TODO raise NoMethodError if data_type doesn't have to_array() and from_array methods

    @property
    def path(self) -> str:
        """Access the file path property
        Returns
        =======
            str
        The path to the file"""

        return self._path
    
    @property
    def data(self):
        """Access the data property"""
        return self._data

    @property
    def loaded(self):
        """Access the loaded property"""
        return self._loaded

    def load(self):
        """Load the steps.bin file"""

        if os.path.exists(self._path):
            # TODO raise warning if load fail
            # Loading the steps
            with open(self._path, 'rb') as file:
                self._steps = pickle.load(file)
        else:
            # Init empty generation steps
            self._steps = {}
            self._step = -1
        self._loaded = True

    def save(self):
        """Save the steps into steps.bin file"""

        # Raise Warning if the save failed
        with open(self._path, 'wb') as file:
            pickle.dump(self._steps, file)

    def init_data(self, *args, **kwargs):
        """Initialize the data or retrieve it from the bin file
        Parameters
        ==========
        Whatever the data type init takes as parameters
        Returns
        =======
            data_type
        Object of given data type"""

        self._data = None
        if self._enabled and self._step in self._steps:
            self._data = self._data_type.from_array(self._steps[self._step])
        if self._data is None:
            self._data = self._data_type(*args, **kwargs)
            self._step = -1
        return self._data

    def make_step(self, step: int) -> object:
        """If the step is loaded and before the current generation step, it loads it elses it run it.
        Use
        ===
        This method is a decorator
        ```
        @a_generation_step_manager_object.load_step(2)
        def do_something():
            #Do something
            return result_of_data_type
        do_something()
        ```

        Parameters
        ==========
            step: int
        The step of the function.
        Returns
        =======
            data_type
        The object of data type or what the function return."""

        def _decorator(func):
            if self._enabled:
                def g(*args, **kwargs):
                    # Run the function if the wanted step is higher than
                    # the current step
                    if step > self._step:
                        result = func(*args, **kwargs)
                        # TODO Raise TypeError if result isn't the same type as data_type
                        self._add_step(step, result)
                        return result
                g.__name__ == func.__name__
                return g
            else:
                return func
        return _decorator

    def _add_step(self, step: int, data: object):
        """Add the step/data couple to the steps data
        Parameters
        ==========
            step: int
        Step id
            data: object of data_type
        Data to associate to the step"""

        # TODO raise warning if step already exists
        self._steps[step] = data.to_array()
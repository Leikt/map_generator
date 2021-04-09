#! /usr/bin/env python3
# coding: utf-8

class Area():
    """Class that make coordinates iterable
    Parameters
    ==========
        width: int
    The width of the area
        height: int
    The height of the area
    Exemple
    =======
    ```
    a = Area(100, 150)
    for x, y in a:
        print(x, y) #> 0,0 / 1,0 / 2,0 ...
    ```
    """

    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height
        self._surface = width * height

    @property
    def width(self) -> int:
        """Access the width property"""
        return self._width

    @property
    def height(self) -> int:
        """Access the height property"""
        return self._height

    @property
    def surface(self) -> int:
        """Access the surface property"""
        return self._surface

    def valid(self, x: int, y: int) -> bool:
        """Test if the given coordinates are in the area
        Parameters
        ==========
            x: int
        The X coordinate to test
            y: int
        The Y coordinate to test
        Returns
        =======
            bool
        True if the coordinate are in the area"""

        return 0 <= x < self._width and 0 <= y < self._height

    def __iter__(self):
        iX = 0
        iY = 0
        height = self._height
        width = self._width
        while iY < height:
            yield iX, iY
            iX += 1
            if iX >= width:
                iX = 0
                iY += 1

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
        self.__width = width
        self.__height = height
        self._surface = width * height

    @property
    def width(self) -> int:
        """Access the width property"""
        return self.__width

    @property
    def height(self) -> int:
        """Access the height property"""
        return self.__height

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

        return 0 <= x < self.__width and 0 <= y < self.__height

    def __iter__(self):
        x = 0
        y = 0
        height = self.__height
        width = self.__width
        while y < height:
            yield x, y
            x += 1
            if x >= width:
                x = 0
                y += 1

class OffsetedArea(Area):
    def __init__(self, width: int, height: int, offset_x: int, offset_y: int):
        Area.__init__(self, width, height)
        self.__offset_x = offset_x
        self.__offset_y = offset_y
        self.__end_x = offset_x + width
        self.__end_y = offset_y + height

    @property
    def offset_x(self):
        """Access the offset_x property"""
        return self.__offset_x

    @property
    def offset_y(self):
        """Access the offset_y property"""
        return self.__offset_y

    
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

        return self.__offset_x <= x < self.__end_x and self.__offset_y <= y < self.__end_y

    def __iter__(self):
        x = self.__offset_x
        y = self.__offset_y
        while y < self.__end_y:
            yield x, y
            x += 1
            if x >= self.__end_x:
                x = self.__offset_x
                y += 1

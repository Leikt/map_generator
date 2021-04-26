import numpy

def resize_data(data: numpy.array, data_width: int, data_height: int, factor: int) -> [numpy.array, int, int]:
    """Resize a 2D array to a bigger 2D array
    Parameters
    ==========
        data: numpy.array
    An numpy array
        data_width: int
    Dimension of the array
        data_height: int
    Dimension of the array
        factor: int
    Size factor between new data and the older one
    Returns
    =======
        numpy.array, int, int
    The new array and its dimensions"""

    # Init
    new_data_width = data_width * factor
    new_data_height = data_height * factor
    new_data = numpy.zeros((new_data_width, new_data_height))

    # Create the new data set
    for x in range(new_data_width):
        for y in range(new_data_height):
            new_data[x, y] = data[int(x / factor), int(y / factor)]
    
    # Results
    return new_data, new_data_width, new_data_height
import logging
import unittest

import src.raw.erosion as erosion
from src.raw.heightmap import Heightmap

logging.basicConfig(level=logging.DEBUG)

class Test_Erosion(unittest.TestCase):
    PARAMETERS = {
        "droplets": 30000,
        "brush_radius": 3,
        "inertia": 0.05,
        "sediment_capacity_factor": 4,
        "sediment_min_capacity": 0.1,
        "erode_speed": 0.3,
        "deposit_speed": 0.3,
        "evaporate_speed": 0.01,
        "gravity": 4.0,
        "droplet_lifetime": 30,
        "initial_water_volume": 1,
        "initial_speed": 1,
        "sea_level": 0
    }

    def test_height_and_gradient(self):
        # Create test heightmap
        heightmap = Heightmap(10, 10)
        heightmap[0, 0] = 1
        heightmap[4, 5] = 1
        heightmap[4, 6] = 0.1
        heightmap[4, 4] = 1
        heightmap[3, 5] = 0.1
        heightmap[2, 5] = 0.5

        e = erosion.Erosion(heightmap, seed=1, **self.PARAMETERS)
        hag = erosion.HeightAndGradient()
        e.calculate_height_and_gradient(hag, heightmap, 0, 0)
        self.assertEqual(hag.height, 1.0)
        self.assertEqual(hag.gradient_x, -1.0)
        self.assertEqual(hag.gradient_y, -1.0)

        e.calculate_height_and_gradient(hag, heightmap, 4, 4)
        self.assertEqual(hag.height, 1.0)
        self.assertEqual(hag.gradient_x, -1.0)
        self.assertEqual(hag.gradient_y, -1.0)
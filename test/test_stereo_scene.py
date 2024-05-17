import unittest
from src.stereo_scene import StereoScene
import numpy as np


def init_StereoScene(rows, cols, captures):
    """
    :param rows: (int) rows in depth map
    :param cols: (int) columns in depth map
    :param captures: (cv2.imread()) tuple of cv2 reads
    :return: (StereoScene) StereoScene object with mock depth map
    """
    return StereoScene(np.arange(rows * cols).reshape(rows, cols), captures)


class TestDepthMap(unittest.TestCase):

    def test_dm_get_shape(self):
        scene = init_StereoScene(6, 6, None)
        self.assertEqual(scene.dm_get_shape(), (6, 6))

        scene = init_StereoScene(8, 3, None)
        self.assertEqual(scene.dm_get_shape(), (8, 3))

        scene = init_StereoScene(3, 8, None)
        self.assertEqual(scene.dm_get_shape(), (3, 8))

        # Minimum depth map 2D array condition
        scene = init_StereoScene(1, 1, None)
        self.assertEqual(scene.dm_get_shape(), (1, 1))

        self.assertRaises(ValueError, StereoScene, [[]], None)  # Depth map not 2D array
        self.assertRaises(ValueError, StereoScene, None, None)  # No depth map

    def test_dm_reduce(self):
        scene = init_StereoScene(8, 6, None)
        scene.dm_reduce(5, 2)
        self.assertEqual(scene.dm_get_shape(), (5, 6))

        scene = init_StereoScene(8, 6, None)
        scene.dm_reduce(2, 5)
        self.assertEqual(scene.dm_get_shape(), (8, 5))

        scene = init_StereoScene(14, 29, None)
        scene.dm_reduce(5, 7)
        self.assertEqual(scene.dm_get_shape(), (10, 28))

        scene = init_StereoScene(15, 15, None)
        scene.dm_reduce(5, 5)
        self.assertEqual(scene.dm_get_shape(), (15, 15))

        scene = init_StereoScene(8, 6, None)
        self.assertRaises(ValueError, scene.dm_reduce, 0, 0)  # Reduce for 0 cells
        self.assertRaises(ValueError, scene.dm_reduce, -1, -1)  # Reduce for negative cells


if __name__ == '__main__':
    unittest.main()

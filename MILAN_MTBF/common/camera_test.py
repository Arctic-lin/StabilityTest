import unittest

import utils
from camera import Camera


class CameraTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = Camera(device_id, 'camera')
        c.setup()

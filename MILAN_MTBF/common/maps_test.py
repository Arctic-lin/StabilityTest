import unittest

import utils
from maps import GoogleMap


class GoogleMapTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = GoogleMap(device_id, 'maps')
        c.setup()

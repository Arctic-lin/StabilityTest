import unittest

import utils
from gallery_tcl import Gallery


class GalleryTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = Gallery(device_id, 'gallery')
        c.setup()

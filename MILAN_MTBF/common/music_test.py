import unittest

import utils
from google_music import Music


class MusicTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = Music(device_id, 'music')
        c.setup()

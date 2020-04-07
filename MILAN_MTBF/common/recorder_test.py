import unittest

import utils
from recorder import Recorder


class RecorderTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = Recorder(device_id, 'recorder')
        c.setup()

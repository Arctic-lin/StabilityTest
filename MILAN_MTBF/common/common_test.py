import unittest

import utils
from common import Common


class CommonTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = Common(device_id, 'common')
        c.save_fail_img()

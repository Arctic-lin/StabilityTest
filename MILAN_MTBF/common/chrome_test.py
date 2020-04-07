import unittest

import utils
from chrome import Chrome


class ContactsTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = Chrome(device_id, 'chrome')
        c.setup()

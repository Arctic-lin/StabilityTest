import unittest

import utils
from message import Message


class MessageTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = Message(device_id, 'message')
        c.setup()


    def test_delete_extra_msg(self):
        device_id = utils.get_connected_device()
        c = Message(device_id, 'message')
        c.delete_extra_msg()

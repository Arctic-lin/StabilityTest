import unittest

import utils
from telephony import Telephony


class ContactsTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = Telephony(device_id, 'contacts')
        c.setup()


    def test_delete_all_contacts(self):
        device_id = utils.get_connected_device()
        c = Telephony(device_id, 'contacts')
        c.delete_all_contacts()

    def test_delete_contact(self):
        device_id = utils.get_connected_device()
        c = Telephony(device_id, 'contacts')
        c.delete_contact('Auto01_24531', False)
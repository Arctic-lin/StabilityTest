import unittest

import utils
from contacts import Contacts


class ContactsTest(unittest.TestCase):

    def test_setup(self):
        device_id = utils.get_connected_device()
        c = Contacts(device_id, 'contacts')
        c.setup()


    def test_delete_all_contacts(self):
        device_id = utils.get_connected_device()
        c = Contacts(device_id, 'contacts')
        c.delete_all_contacts()

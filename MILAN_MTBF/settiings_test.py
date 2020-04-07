import os
import sys
import unittest

from common.settings import Settings

lib_path = os.path.dirname(os.path.abspath(__file__))
if lib_path not in sys.path:
    sys.path.append(lib_path)


class SettingsTest(unittest.TestCase):

    def test_enableProductivityEdge(self):
        device_id = '5000004945'
        s = Settings(device_id, '123')
        s.enableProductivityEdge(False)

    def test_get_battery_level(self):
        device_id = '5000004945'
        s = Settings(device_id, '123')
        level = s._get_battery_level()
        print(level)

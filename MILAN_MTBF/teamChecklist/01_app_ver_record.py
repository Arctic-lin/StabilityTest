#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
this is for recording app versions

"""

from __future__ import division

import json
import os
import subprocess
import sys
import unittest
from ConfigParser import ConfigParser

import requests

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)

from common.settings import Settings


class TestAppVer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        is_tat_test = os.environ.get("MDEVICE")
        if is_tat_test:
            serino_m = "MDEVICE"
            # serino_s = "SDEVICE"
            cls.mdevice_id = os.environ.get(serino_m)
            # cls.sdevice_id = os.environ.get(serino_s)
        else:
            serino_m = sys.argv[1]
            # serino_s = sys.argv[2]
            cls.mdevice_id = serino_m
            # cls.sdevice_id = serino_s

        cls.mod = Settings(serino_m, "settings")

        cls.scriptPath = sys.path[0]
        cls.apk_path = os.path.join(cls.scriptPath, "apkinfo.apk")

        cls.info_2_tat = {}

    @classmethod
    def tearDownClass(cls):
        pass
        # cls.mod.clear_notification()
        # cls.mod_s.clear_notification()
        # cls.mod.logger.debug("BBM Mission Complete")

    def setUp(self):
        pass
        # self.mod.back_to_home()
        # self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def tearDown(self):
        pass

    def test_1_app_ver_record(self):
        """
        run appinfo.apk, get device info from device
        """
        self.mod.adb.shell('settings put global verifier_verify_adb_installs 0')

        # install app
        self.mod.logger.debug("install app info")
        cmd = "adb -s %s install -r -g %s" % (self.mdevice_id, self.apk_path)
        command(cmd)

        # generate permissions
        self.mod.adb.shell('pm grant tct.nb.performance.apkinformation android.permission.WRITE_EXTERNAL_STORAGE')
        self.mod.adb.shell('pm grant tct.nb.performance.apkinformation android.permission.READ_EXTERNAL_STORAGE')

        # start service
        self.mod.adb.shell('am startservice tct.nb.performance.apkinformation/.AppInfoManager')
        self.mod.device.delay(4)
        self.mod.adb.shell('am stopservice tct.nb.performance.apkinformation/.AppInfoManager')

        # uninstall app
        self.mod.logger.debug("install app info")
        cmd = "adb -s %s uninstall tct.nb.performance.apkinformation" % self.mdevice_id
        command(cmd)

        # pull result
        self.mod.logger.debug("pull data")
        cmd = "adb -s %s pull /sdcard/monkeypicture %s" % (self.mdevice_id, self.scriptPath)
        command(cmd)

        # generate data for TAT server
        self.fmt_data_4_TAT()

    def fmt_data_4_TAT(self):
        ver = self.mod.adb.get_device_version()

        result_path = os.path.join(self.scriptPath, 'monkeypicture', 'Results.txt')

        if not os.path.exists(result_path):
            return None

        config = ConfigParser()
        config.read(result_path)
        ret = {}
        ignore_kw = ('qualcomm.', 'qti.', 'example.')
        for sec in config.sections():
            if sec in ignore_kw:
                continue
            ret[sec] = (config.get(sec, "AppLabel"), config.get(sec, "AppVersion"))

        for k, v in ret.items():
            self.mod.logger.info("%s %s" % (k, v))

        # dump to json file
        self.info_2_tat['project'] = sys.argv[2]  # project name MUST be same as TAT server
        self.info_2_tat['sw_ver'] = ver
        self.info_2_tat['app_vers'] = json.dumps(ret)  # add json fmt, app_package: (app_label, app_ver)
        jsonfile = os.path.join(self.scriptPath, 'app_ver.json')
        self.dump_to_file(self.info_2_tat, jsonfile)

        # upload to server
        self.upload_to_server()

    def upload_to_server(self):
        server_path = sys.argv[3]  # server path, get from input
        requests.post(server_path, self.info_2_tat)

    def dump_to_file(self, dump, filepath):
        with open(filepath, "w", ) as f_dump:
            json.dump(dump, f_dump)


def command(cmd):
    p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p1.wait()


if __name__ == "__main__":
    # unittest.main()
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestAppVer)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)

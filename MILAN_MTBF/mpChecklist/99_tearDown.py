#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: 99_tearDown.py
@time: 2017/10/12 9:37

information about this file
"""

from __future__ import division

import os
import shutil
import sys
import unittest
import xml.etree.ElementTree as ET

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)

from common.settings import Settings
from common.crash_utils import get_crash
from TclTools.GetSystemProperty import get_system_properties
from TclTools.MailHelper import MailHelper
from TclTools.XmlHelper import XmlHelper


class TestTearDown(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        serino_m = "MDEVICE"
        # serino_m = "1163805830"

        cls.mod = Settings(serino_m, "settings")

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_send_report(self):
        """
        read from log_path//test_result.txt
        generate report and send to team
        :return:
        """
        loops_show_properties = self.generate_property_table()
        # loops_show_results = self.generate_result_table()
        sw = self.mod.adb.get_device_version()
        variant = self.mod.adb.get_product_name()
        net = 'Z:'
        desk = r'\08_Share\00_PerformanceReport\Athena\05_Customization\MPChecklist' + os.sep + sw + '_' + variant
        net_desk = net + desk
        net_desk_img = net + desk + os.sep + 'fail_img'
        if not os.path.exists(net_desk):
            # os.mkdir(net_desk)
            # os.mkdir(net_desk_img)
            os.makedirs(net_desk_img)
        try:
            mpchecklist_new = self.mod.log_path + os.sep + 'mpchecklist_new.html'
            shutil.copy(mpchecklist_new, net_desk)

            screenshot_folder = self.mod.log_path + os.sep + 'fail_img'
            screenshots = [screenshot_folder + os.sep + screenshot_path for screenshot_path in
                           os.listdir(screenshot_folder)]
            for screenshot in screenshots:
                shutil.copy(screenshot, net_desk_img)
        except:
            self.mod.logger.error("******* copy report/screenshot to net desk failed ******")
        http_desk = r'\\172.16.11.11\val' + desk + os.sep + 'mpchecklist_new.html'
        loops_show_results = http_desk
        crashed = get_crash(self.mod.log_path)
        mail = MailHelper()
        # html = self.generate_html_for_mp()
        # mail.mail_test_finished_for_mp(html)
        mail.mail_test_finished(loops_show_properties=loops_show_properties, loops_show_results=loops_show_results,
                                crashed=crashed)

    def generate_html_for_mp(self):
        html = ""
        result_path = os.environ.get("LOG_PATH")
        if result_path is None:
            result_path = os.path.dirname(os.path.dirname(__file__)) + "\\results"

        report = result_path + r"\mpchecklist.html"
        with open(report) as template:
            html = template.readlines()
        return "".join(html)

    def generate_property_table(self):
        """
        generate a table include property information
        :return:
        """
        xml = XmlHelper()
        serino = xml.get_property_from_xml(elem_tag="serino", elem_attrib="value")
        property_name, property_key, property_value = get_system_properties(serino)
        temp_list = ["<tr><td>%s</td><td>%s</td></tr>" % (name, value) for name, value in
                     zip(property_name, property_value)]
        loops_show_properties = "".join(temp_list)
        return loops_show_properties

    def generate_result_table(self):
        """
        generate html table for automatic test cases from test_result.xml
        :return:
        """
        html_table_body = ""
        tree = ET.ElementTree(file=self.mod.result_file_path)
        for elem in tree.iter(tag='testcase'):
            casename = elem.attrib["casename"]
            result = elem.attrib["testresult"]
            test_type = "AutoTest"
            if "testtype" in elem.attrib:
                test_type = elem.attrib["testtype"]
            test_date = ""
            if "testdata" in elem.attrib:
                test_date = elem.attrib["testdata"]

            failure_elem = elem.find("failure")
            failure_msg = ""
            if failure_elem is not None:
                failure_msg = failure_elem.attrib["message"]
            else:
                failure_msg = test_date
            # print casename, result, failure_msg
            html_table_body += "<tr>" \
                               "<td>" + casename + "</td>"

            if result == "FAIL":
                html_table_body += "<td style='text-align:center'>" \
                                   "<span style='background:red;mso-highlight:red'>" + result + "</ span></td>"
            elif result.lower() == "to check":
                html_table_body += "<td style='text-align:center'>" \
                                   "<span style='background:red;mso-highlight:yellow'>" + result + "</ span></td>"
            else:
                html_table_body += "<td style='text-align:center'>" + result + "</td>"

            if test_type.lower() == "manual":
                html_table_body += "<td>ManualTest</td>"
            else:
                html_table_body += "<td>AutoTest</td>"

            html_table_body += "<td>" + failure_msg + "</td></tr>"
        return html_table_body


if __name__ == "__main__":
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestTearDown)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)

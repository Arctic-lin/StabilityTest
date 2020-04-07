#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: GetSystemProperty.py
@time: 2017/10/20 15:06

information about this file
"""

import os
import subprocess
import sys

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)

from common.configs import GetConfigs
from XmlHelper import *


def perform_cmd(serino, value):
    """
    perform adb shell getprop
    :param serino:
    :param value:
    :return:
    """
    cmd = "adb -s %s shell getprop %s" % (serino, value)
    # print cmd
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    proc.wait()
    print "stdout:", stdout
    return stdout


def set_system_property(serino):
    """
    set property,
    :return:
    """
    property_name, property_key, property_value = get_system_properties(serino)

    # write data to xml
    xml.set_result(property_name, property_key, property_value)

    return property_name, property_value


def get_system_properties(serino):
    """
    get properties name from common.ini
    :param serino:
    :return: 3 list, name, key, value(return from perform adb shell) project_name = ro.hwf.nfc.tuning_config
    """
    # get all options from section sysProperty
    config = GetConfigs("common")
    property_name = config.get_all_options("sysProperty")
    print property_name

    # get all values from option
    property_key = [config.get("sysProperty", option) for option in property_name]
    print property_key

    # perform adb shell getprop + value, get returned value
    property_value = [perform_cmd(serino, value).strip() for value in property_key]
    print property_value

    return property_name, property_key, property_value


if __name__ == '__main__':
    xml = XmlHelper()

    # get parameters
    serino = sys.argv[1]  # device id
    email_list_for_mp = sys.argv[2]
    email_list_for_smoke = sys.argv[3]
    branch_for_smoke = sys.argv[4]
    device_for_smoke = sys.argv[5]
    test_plan_type = sys.argv[6]

    assert "mpchecklist" in test_plan_type.lower() or "smoke" in test_plan_type.lower(), "test type should be mpChecklist or smoke, but %s got" % test_plan_type

    # set all date
    set_system_property(serino)

    # set other data
    xml.set_data(elem_tag="serino", elem_attrib="value", value=serino)
    xml.set_data(elem_tag="email_list_for_mp", elem_attrib="value", value=email_list_for_mp)
    xml.set_data(elem_tag="email_list_for_smoke", elem_attrib="value", value=email_list_for_smoke)
    # xml.set_data(elem_tag="branch_for_smoke", elem_attrib="value", value=branch_for_smoke)
    xml.set_data(elem_tag="device_for_smoke", elem_attrib="value", value=device_for_smoke)
    xml.set_data(elem_tag="test_plan_type", elem_attrib="value", value=test_plan_type)
    xml.set_data(elem_tag="project_name", elem_attrib="value", value=device_for_smoke)

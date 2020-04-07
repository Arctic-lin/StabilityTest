#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
deal with html report
"""
import os
import shutil
import sys

import common.log_utils

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)
from common import common


def modify_html_report(case_name, test_result="PASS", smoke=True):
    """
    load template, replace test result by case name
    :param case_name:
    :param test_result:
    :param smoke:
    :return:
    """
    case_id = case_name.split("_")[0]
    test_result = "PASS" if (test_result or test_result == "PASS") else "FAIL"
    print "set result of case <%s> %s" % (case_name, test_result)
    if test_result == "FAIL":
        return False

    file_data = ""
    result_path = common.log_utils.create_folder()

    html_templates = os.path.dirname(os.path.dirname(__file__)) + "\\TclTools\\templates\\smoke.html" if smoke \
        else os.path.dirname(os.path.dirname(__file__)) + "\\TclTools\\templates\\mpchecklist.html"
    html_result = result_path + "\\smoke_result.html" if smoke else result_path + "\\mpchecklist.html"

    if not os.path.exists(html_result):
        shutil.copy(html_templates, html_result)

    with open(html_result, "r", ) as f:
        for line in f:
            if case_id in line:
                line = line.replace(" style='background:red;mso-highlight:red'>FAIL", ">%s" % test_result)
            file_data += line
    with open(html_result, "w") as f:
        f.write(file_data)


def modify_html_report_kwd(smoke=False, **kwargs):
    """
    load template, replace keywords
    :param smoke: whether is smoke test
    :param kwargs:
    :return:
    """
    file_data = ""
    result_path = common.log_utils.create_folder()

    html_templates = os.path.dirname(os.path.dirname(__file__)) + "\\TclTools\\templates\\smoke.html" if smoke \
        else os.path.dirname(os.path.dirname(__file__)) + "\\TclTools\\templates\\mpchecklist.html"
    html_result = result_path + "\\smoke_result.html" if smoke else result_path + "\\mpchecklist.html"

    if not os.path.exists(html_result):
        shutil.copy(html_templates, html_result)

    with open(html_result, "r", ) as f:
        for line in f:
            for old_value, new_value in kwargs.items():
                if old_value in line:
                    line = line.replace(old_value, new_value)
            file_data += line
    with open(html_result, "w") as f:
        f.write(file_data)

    return file_data


if __name__ == '__main__':
    modify_html_report("267788")
    modify_html_report("275730(Without AFW)")

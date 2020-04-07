#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: XmlHelper.py
@time: 2017/10/24 10:00

information about this file
"""

from __future__ import division

import os
import sys
import traceback
from xml.dom.minidom import Document
from xml.etree.ElementTree import ElementTree, Element

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)


class XmlHelper(object):
    """
    this class can help you generate xml, create element/tag/attrib, get value via tag and so on
    """

    def __init__(self, file_path="property_info.xml"):
        log_path = os.path.dirname(os.path.abspath(__file__))
        # log_path = sys.path[0][sys.path[0].find(':') + 1:] + '\\results'
        self.file_path = log_path + os.sep + file_path
        print self.file_path
        if not os.path.exists(self.file_path):
            self.create_file()

    def create_file(self, root="properties"):
        """
        do not check the file exist or not, it will create new file rudely!
        :param root:
        :return:
        """
        self.doc = Document()
        root = self.doc.createElement(root)  # 创建根元素
        self.doc.appendChild(root)
        with open(self.file_path, "w") as f:
            f.write(self.doc.toprettyxml(indent=''))

    def set_result(self, tags, attrib1_values, attrib2_values, attrib1="property_key", attrib2="value"):
        """
        set result to xml
        :param tags: tag list
        :param attrib1_values: value1 list
        :param attrib2_values: value2 list
        :param attrib1: attrib 1
        :param attrib2: attrib 2
        :return:
        """
        tree = ElementTree()
        tree.parse(self.file_path)
        root = tree.getroot()  # get root
        for tag, attrib1_value, attrib2_value in zip(tags, attrib1_values, attrib2_values):
            self.remove_elem_if_needed(root, tag)
            element = Element(tag, {attrib1: attrib1_value, attrib2: attrib2_value})  # create element testcase, attrib
            root.append(element)

        tree.write(self.file_path, encoding='utf-8', xml_declaration=True)

    def set_data(self, elem_tag, elem_attrib, value):
        """
        set date to xml,
        :param elem_tag:
        :param elem_attrib:
        :param value:
        :return:
        """
        tree = ElementTree()
        tree.parse(self.file_path)
        root = tree.getroot()  # get root

        # it the target elem exist in the xml, remove it,
        self.remove_elem_if_needed(root, elem_tag)

        element = Element(elem_tag, {elem_attrib: value})  # create element testcase, attrib
        root.append(element)
        tree.write(self.file_path, encoding='utf-8', xml_declaration=True)

    def remove_elem_if_needed(self, root, elem_tag):
        """
        check the tag exist or not, if exist, remove them
        :param elem_tag:
        :return:
        """
        for elem in root.iter(elem_tag):
            root.remove(elem)

    def get_property_from_xml(self, elem_tag, elem_attrib, single_value=True):
        """
        get data form xml
        :param elem_tag: xml tag
        :param elem_attrib: xml attrib
        :param single_value: get only one value if true, get all values in a list if false
        :return:  return None, if get exception
        """
        try:
            tree = ElementTree()
            tree.parse(self.file_path)

            if single_value:
                for elem in tree.iter(tag=elem_tag):
                    return elem.attrib[elem_attrib]
            else:
                return [elem.attrib[elem_attrib] for elem in tree.iter(tag=elem_tag)]
        except:
            print traceback.format_exc()
            return None


if __name__ == '__main__':
    pass

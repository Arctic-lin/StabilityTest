# -*- coding: UTF-8 -*-

import sys, os
from configparser import ConfigParser

class GetConfigs(object):
    """Get a option value from a given section."""
    
    def __init__(self, module):
        self.commonconfig = ConfigParser()
        commonPath = sys.path[0] + "\\lib\\common.ini"
        if not os.path.exists(commonPath):
            commonPath = sys.path[0] + "\\common.ini"
        self.commonconfig.read(commonPath)
        self.testtype = self.commonconfig.get("Default","TEST_TYPE").upper()        
        self.module = module.capitalize()
        
    def getint(self, section, option, filename, exc=0):
        """return an integer value for the named option.
        return exc if no the option. 
        """
        config = ConfigParser()
        try:
            config.read(sys.path[0] + "\\common\\"+ filename + ".ini")
            return config.getint(section, option)
        except:
            return exc
        
    def getstr(self, section, option, filename, exc=None):
        """return an string value for the named option."""
        config = ConfigParser()
        try:
            config.read(sys.path[0] + "\\common\\"+filename + ".ini")
            return config.get(section,option)
        except:
            return exc
        
    def get_test_times(self):
        """return a dict with name:value for each option
        in the section.
        """
        #mini test will run 5m, full run 2h
        if self.testtype == "MINI":
            return 60
        else:
            return 7200

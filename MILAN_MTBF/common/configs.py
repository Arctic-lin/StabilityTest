import os
from ConfigParser import ConfigParser


class Configs(object):
    def __init__(self, module):
        self.config = ConfigParser()
        self.config.read(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configure", "%s.ini" % module))

    def set_section(self, section):
        self.section = section

    def get(self, option, section=None):
        """return an string value for the named option."""
        if section == None and getattr(self, "section"):
            section = self.section
        try:
            try:
                return self.config.getint(section, option) or None
            except:
                return self.config.get(section, option).strip('\'').strip('\"') or None
        except:
            return None


class AppConfig(Configs):

    def __call__(self, *args, **kwargs):
        return self.get(*args)

    def id(self, option, section=None):
        try:
            return "%s:%s" % (
                self.get("package", section).strip('\'').strip('\"'), self.get(option, section).strip('\'').strip('\"'))
        except:
            return None


class GetConfigs(object):
    """Get a option value from a given section."""

    def __init__(self, module):
        self.commonconfig = ConfigParser()
        if module.lower() == "mp_checklist":
            self.commonconfig.read(
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mpChecklist", "project.ini"))
        elif module.lower() == "smoke":
            self.commonconfig.read(
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configure", "smoke.ini"))
        else:
            self.commonconfig.read(
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configure", "common.ini"))
            self.testtype = self.commonconfig.get("Default", "TEST_TYPE").upper()
            self.networktype = self.commonconfig.get("Default", "NETWORK_TYPE")
            self.site = self.commonconfig.get("Default", "SITE").upper()
            self.module = module.capitalize()

    def get(self, section, option):
        try:
            return self.commonconfig.get(section, option) or None
        except:
            return None

    def get_all_options(self, section):
        ret = self.commonconfig.options(section)
        return ret

    @staticmethod
    def getstr(section, option, filename, exc=None):
        """return an string value for the named option."""
        config = ConfigParser()
        try:
            config.read(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configure",
                                     "%s.ini" % filename))
            return config.get(option, section)
        except Exception, e:
            print e
            return exc

    @staticmethod
    def getint(section, option, filename, exc=0):
        """return an integer value for the named option.
        return exc if no the option. 
        """
        config = ConfigParser()
        try:
            config.read(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configure",
                                     "%s.ini" % filename))
            return config.getint(section, option)
        except:
            return exc

    def get_test_times(self):
        """return a dict with name:value for each option
        in the section.
        """
        config = ConfigParser()
        if self.testtype == "STABILITY" or self.testtype == "MINI":
            config_name = '{}_{}.ini'.format(self.testtype.capitalize(), self.networktype)
        else:
            config_name = '{}.ini'.format(self.testtype.capitalize())
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   "configure",
                                   config_name)
        config.read(config_path)
        item = config.items(self.module)
        return dict(item)


if __name__ == '__main__':
    config = AppConfig("appinfo", "Sprints")
    print config.id("id_search", "Email")

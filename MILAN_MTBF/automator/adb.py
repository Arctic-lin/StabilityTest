# -*- coding: UTF-8 -*-

import os
import re
# from common.simcard import *
import smtplib
import subprocess
import time
from email.mime.text import MIMEText

mail_host = "mail.tcl.com"
mail_user = "atttest02@tcl.com"
mail_pass = "StabilityTest02"


def send_mail_exception(To, device):
    msg = MIMEText('zxcvbnm', _subtype="plain", _charset="utf-8")
    msg["Subject"] = "%s device not connected" % device
    msg["From"] = mail_user
    msg["To"] = To
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, To, msg.as_string())
        server.close()
        return True
    except Exception, e:
        return False


class Adb(object):

    def __init__(self, serial=None, adb_server_host=None, adb_server_port=None):
        self.__adb_cmd = None
        self.default_serial = serial if serial else os.environ.get("ANDROID_SERIAL", None)
        self.adb_server_host = str(adb_server_host if adb_server_host else '127.0.0.1')
        self.adb_server_port = str(adb_server_port if adb_server_port else '5037')
        self.adbHostPortOptions = []
        if self.adb_server_host not in ['localhost', '127.0.0.1']:
            self.adbHostPortOptions += ["-H", self.adb_server_host]
        if self.adb_server_port != '5037':
            self.adbHostPortOptions += ["-P", self.adb_server_port]

    def adb(self):
        if self.__adb_cmd is None:
            if "ANDROID_HOME" in os.environ:
                filename = "adb.exe" if os.name == 'nt' else "adb"
                adb_cmd = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", filename)
                if not os.path.exists(adb_cmd):
                    raise EnvironmentError(
                        "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
            else:
                import distutils
                if "spawn" not in dir(distutils):
                    import distutils.spawn
                adb_cmd = distutils.spawn.find_executable("adb")
                if adb_cmd:
                    adb_cmd = os.path.realpath(adb_cmd)
                else:
                    raise EnvironmentError("$ANDROID_HOME environment not set.")
            self.__adb_cmd = adb_cmd
        return self.__adb_cmd

    def cmd(self, *args, **kwargs):
        '''adb command, add -s serial by default. return the subprocess.Popen object.'''
        serial = self.device_serial()
        if serial:
            if " " in serial:  # TODO how to include special chars on command line
                serial = "'%s'" % serial
            return self.raw_cmd(*["-s", serial] + list(args))
        else:
            return self.raw_cmd(*args)

    def raw_cmd(self, *args):
        '''adb command. return the subprocess.Popen object.'''
        cmd_line = [self.adb()] + self.adbHostPortOptions + list(args)
        if os.name != "nt":
            cmd_line = [" ".join(cmd_line)]
        cmd_line_str = " ".join(cmd_line)
        # print 'cmd: {}'.format(cmd_line_str)
        return subprocess.Popen(cmd_line_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def device_serial(self):
        if not self.default_serial:
            devices = self.devices()
            if devices:
                if len(devices) is 1:
                    self.default_serial = list(devices.keys())[0]
                else:
                    raise EnvironmentError("Multiple devices attached but default android serial not set.")
            else:
                raise EnvironmentError("Device not attached.")
        return self.default_serial

    def devices(self):
        '''get a dict of attached devices. key is the device serial, value is device name.'''
        out = self.raw_cmd("devices").communicate()[0].decode("utf-8")
        match = "List of devices attached"
        index = out.find(match)
        if index < 0:
            raise EnvironmentError("adb is not working.")
        return dict([s.split("\t") for s in out[index + len(match):].strip().splitlines() if s.strip()])

    def forward(self, local_port, device_port):
        '''adb port forward. return 0 if success, else non-zero.'''
        return self.cmd("forward", "tcp:%d" % local_port, "tcp:%d" % device_port).wait()

    def forward_list(self):
        '''adb forward --list'''
        version = self.version()
        if int(version[1]) <= 1 and int(version[2]) <= 0 and int(version[3]) < 31:
            raise EnvironmentError("Low adb version.")
        lines = self.raw_cmd("forward", "--list").communicate()[0].decode("utf-8").strip().splitlines()
        return [line.strip().split() for line in lines]

    def version(self):
        '''adb version'''
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", self.raw_cmd("version").communicate()[0].decode("utf-8"))
        print self.raw_cmd("version").communicate()[0].decode("utf-8")
        return [match.group(i) for i in range(4)]

    def shell(self, *args):
        """
        perform adb shell commond
        :param args:
        :return: output in a list
        """
        serial = self.device_serial()
        if serial.find(" ") > 0:  # TODO how to include special chars on command line
            serial = "'%s'" % serial
        cmd_line = ["-s", serial, "shell"] + list(args)
        cmd_line = ['"%s"' % self.adb()] + cmd_line
        proc = subprocess.Popen(" ".join(cmd_line), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
        return stdout
        # serial = self.device_serial()
        # if serial.find(" ") > 0:  #
        #     serial = "'%s'" % serial
        # cmd_line = ["-s", serial,"shell"] + list(args)
        # # sometimes -p -h do not work in my PC, remove below code
        # if self.adb_server_port:  # add -P argument
        #     cmd_line = ["-P", str(self.adb_server_port)] + cmd_line
        # if self.adb_server_host:  # add -H argument
        #     cmd_line = ["-H", self.adb_server_host] + cmd_line
        #
        # cmd_line = ['"%s"'%self.adb()]+cmd_line
        # # print cmd_line
        # return subprocess.Popen(" ".join(cmd_line), stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()

    def shell2(self, *args):
        serial = self.device_serial()
        if serial.find(" ") > 0:  # TODO how to include special chars on command line
            serial = "'%s'" % serial
        cmd_line = ["-s", serial, "shell"] + list(args)
        cmd_line = ['"%s"' % self.adb()] + cmd_line
        proc = subprocess.Popen(" ".join(cmd_line), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
        return stdout, stderr
        # return os.popen(" ".join(cmd_line)).read()

    def bugreport(self, *args):
        serial = self.device_serial()
        if serial.find(" ") > 0:  # TODO how to include special chars on command line
            serial = "'%s'" % serial
        cmd_line = ["-s", serial, "bugreport"] + list(args)
        cmd_line = ['"%s"' % self.adb()] + cmd_line
        cmd_str = " ".join(cmd_line)
        print cmd_str
        proc = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
        return stdout, stderr

    def enter_shell_cmd(self, cmd):
        serial = self.device_serial()
        if serial.find(" ") > 0:  # TODO how to include special chars on command line
            serial = "'%s'" % serial
        cmd_line = ["-s", serial, "shell"]
        cmd_line = ['"%s"' % self.adb()] + cmd_line
        pipe = subprocess.Popen(" ".join(cmd_line), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return_code = pipe.communicate(cmd)
        # print return_code
        return return_code

    def get_device_seriono(self):
        '''
        get device serial
        Usages:
        d.get_device_seriono()
        '''
        return self.shell("getprop ro.serialno").strip()

    def get_device_name(self):
        '''
        get Build.product name
        Usages:
        d.get_device_name()
        '''
        return self.shell("getprop ro.build.product").strip()

    def get_device_version(self):
        '''
        get product version
        Usages:
        d.get_device_version()
        '''
        return self.shell("getprop ro.build.version.incremental").strip()

    def get_device_manufacturer(self):
        '''
        Get manufacturer Info
        Usages:
        d.get_device_manufacturer()
        '''
        return self.shell("getprop ro.product.manufacturer").strip()

    def get_device_brand(self):
        '''
        Get brand Info
        Usages:
        d.get_device_brand()
        '''
        return self.shell("getprop def.tctfw.brandMode.name").strip()

    def get_device_model(self):
        '''
        Get Build.MODEL Info
        Usages:
        d.get_device_model()
        '''
        return self.shell("getprop ro.product.model").strip()

    def get_product_name(self):
        '''
        Get Build.MODEL Info
        Usages:
        d.get_device_model()
        '''
        return self.shell("getprop ro.vendor.product.name").strip()

    def is_cn_variant(self):
        if 'cn' in self.get_product_name():
            return True
        else:
            return False

    def is_uiautomater_installed(self):
        ret = self.shell("pm list package com.github.uiautomator").strip()
        target = ['com.github.uiautomator', 'com.github.uiautomator.test']
        if all([p in ret for p in target]):
            return True
        return False

    def get_prop(self,command):
        """
        Fingerprint_adb shell getprop ro.build.fingerprint
        :return:
        """
        return self.shell("getprop %s"%command).strip()


    def get_current_lang(self):
        '''
        Get language Info
        Usages:
        d.get_current_lang()
        '''
        return self.shell("getprop persist.sys.language").strip()

    def check_fullramdump(self):
        ret = self.shell('ls sdcard').strip()
        for line in ret.split('\n'):
            if 'fullramdump' in line:
                return line[line.find('fullramdump'):].strip()
        return None

    def check_web_file_for_jankiness(self):
        ret = self.shell('ls sdcard').strip()
        for line in ret.split('\n'):
            if 'testdata' in line:
                return True
        return False

    def get_cpuinfo(self):
        '''
        Get cpu Info
        Usages:
        d.get_current_lang()
        '''
        return self.shell("getprop ro.product.cpu.abi").strip()

    def get_sdk(self):
        """
        get sdk
        :return:
        """
        return self.shell("getprop ro.build.version.sdk")

    def call(self, phone):
        '''
        call number
        Usages:
        d.call("10010")      
        '''
        data = self.shell("am start -a android.intent.action.CALL -d tel:%s" % (phone))
        return True

    def get_call_state(self):
        return True

    def send_sms(self, phonenum, smsbody):
        '''
        send sms
        Usages:
        d.send_sms("10010","abcdefg")      
        '''
        data = self.shell("am start -a android.intent.action.SENDTO -d sms:%s --es %s cxye" % (phonenum, smsbody))
        self.shell("adb shell input keyevent 22")
        self.shell("adb shell input keyevent 66")
        return True

    def get_meminfo(self):
        return True

    def get_current_packagename(self):
        return True

    def get_data_connected_status(self):
        ''''get the status of data connection.
        Usages:
        d.get_data_connected_status()      
        '''
        status = self.shell("dumpsys telephony.registry")
        if "mDataConnectionState=2" in status:
            return True
        return True #无法通用

    def get_data_service_state(self, sim=1):
        '''get data service state to judge whether attach the operator network.
        Usages:
        d.get_data_service_state()  
        '''
        print("Check data service status.")
        data = self.shell("dumpsys telephony.registry")
        if not data:
            return None
        # print data


        index = data.find("mServiceState")
        # print index
        if sim == 2:
            index = data.rfind("mServiceState")
        # print index

        if index < 0:
            return None
        index2 = data.find("\n", index)
        assert index2 > 0
        data = data[index:index2 - 1].lower()
        if (data.find("edge") > 0 or data.find("gprs") > 0 or
                data.find("1xrtt") > 0):
            return "2G"
        elif (data.find("evdo") > 0 or data.find("hsupa") > 0 or
              data.find("hsdpa") > 0 or data.find("hspa") > 0):
            return "3G"
        elif data.find("lte") > 0:
            return "LTE"
        else:
            return "UNKNOWN"

    def is_access_network(self):
        '''check if it access the network or not.
        Usages:
        d.get_data_service_state()  
        '''
        data = self.shell("dumpsys telephony.registry")
        if not data:
            return False
        if data.find("mServiceState=0") > -1:
            print("Access the network .")
            return True
        else:
            print("Cannot access the network ")
            return False

    def restart_viewserver(self):
        '''restart viewserver if it no respon
        Usages:
        d.restart_viewserver()  
        '''
        self.shell("dumpsys telephony.registry")
        self.shell("service call window 2")
        time.sleep(2)
        result = self.shell("service call window 3")
        if result.find("00000000 00000000") > -1:
            self.shell("service call window 1 i32 4939")
            time.sleep(2)
            result = self.shell("service call window 3")
            if result.find("00000000 00000001") > -1:
                return True
            else:
                print("Start viewserver fail.")
                return False
        else:
            print("Exit viewserver fail.")
            return False

    def get_telephony_status(self):
        """
        get telephony status, mcallStateֵΪ0����ʾ����״̬��1��ʾ����δ������2��ʾ�绰ռ��״̬
        :return: int 0, 1, 2, -1(no data got)
        """
        ret, _ = self.shell2("dumpsys telephony.registry")
        kw = "mCallState="
        index = ret.find(kw)
        status = -1
        if index > 0:
            status = int(ret[index + len(kw):index + len(kw) + 1])
        print status, type(status)
        return status

    def close_call_service(self):
        ret, error = self.shell2("service call phone 3")
        print ret, "->", error
        if not ret:
            print "***** close call service API do not work *****"
            return False
        if "00000001" in ret:
            print "find unclosed call service, close it "
        else:
            print "no unclosed call service"
        return True

    def is_screen_on(self):
        '''check if the screen is on or not
        Usages:
        d.is_screen_on()  
        '''
        data = self.shell("dumpsys display")
        if data:
            return None
        if data.find("mBlanked=false") > -1:
            return True
        else:
            return False

    def get_file_num(self, path, format):
        '''get number of file with specified format.
        Usages:
        d.is_screen_on()  
        '''
        content = self.shell("ls " + path)
        num = content.count(format)
        #     self._logger.debug("%s file num is %d." % (format,num))
        return num

    def startactivity(self, packet, activity):
        '''start activity by shell
        Usages:
        d.is_screen_on()  
        '''
        data = self.shell("am start -n %s/%s" % (packet, activity))
        if data.find("Error") > -1:
            return False
        return True

    def is_kw_in_shell_output(self, cmd, keywords):
        """
        perform shell cmd, and check the keywords in the output or not
        :param cmd:
        :param keywords:
        :return:
        """
        print "input %s" % cmd
        ret = self.shell(cmd)
        print "output: %s" % ret
        for item in ret:
            if keywords in item:
                return True
        else:
            return False

    def PowerKeyDown(self):
        print "Press PowerKeyDown"
        self.shell('sendevent /dev/input/event3 1 116 1')
        time.sleep(0.1)
        self.shell('sendevent /dev/input/event3 0 0 0')
        time.sleep(1)

    def PowerKeyUp(self):
        print "Press PowerKeyUp"
        self.shell('sendevent /dev/input/event3 1 116 0')
        time.sleep(0.1)
        self.shell('sendevent /dev/input/event3 0 0 0')
        time.sleep(1)

    def LongPressPower(self, longtime=3):
        print "Long Press PowerKey"
        self.PowerKeyDown()
        time.sleep(longtime)
        self.PowerKeyUp()

    def longPressHome(self):
        print 'Long Press home via keycode 3'
        self.shell('input keyevent --longpress 3')

    def battery_level(self):
        ret = self.shell('dumpsys battery')
        # print type(ret), ret
        kw = 'level:'
        start = ret.find(kw)
        end = ret.find(kw) + len(kw) + 4
        if kw in ret:
            return ret[start:end]

        return 'can not find level in dumpsys battery'

    def batery_level_int(self):
        try:
            ret = self.battery_level().split(':')[-1].strip()
            return int(ret)
        except:
            return None

    def input(self, content):
        self.shell("input text %s" % content)

    def dumpsys_meminfo(self):
        status = self.shell("dumpsys meminfo")
        return status

if __name__ == "__main__":
    a = Adb("f049b54f")
    # a.enter_shell_cmd('am start -a com.android.HiddenMenu.START -n com.android.HiddenMenu/com.android.HiddenMenu.HiddenAppTop --es hidden_key "##782#"')
    print a.check_fullramdump()
    # print a.get_device_name()
    # print a.get_device_version()
    # print a.get_device_seriono()
    # print a.get_device_manufacturer()
    #
    # print a.get_device_model()
    # print a.get_current_lang()
    #
    # print a.get_cpuinfo()

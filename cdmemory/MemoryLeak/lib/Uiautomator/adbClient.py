# _*_ coding: UTF-8 _*_
import os
import time
try:
    import cv2
except ImportError:
    print("Cannot import cv2")
import subprocess
import sys
import re
import psutil
from threading import Thread

def U(x):
    if sys.version_info.major == 2:
        return x.decode('utf-8') if type(x) is str else x
    elif sys.version_info.major == 3:
        return x

def param_to_property(*props, **kwprops):
    if props and kwprops:
        raise SyntaxError("Can not set both props and kwprops at the same time.")

    class Wrapper(object):

        def __init__(self, func):
            self.func = func
            self.kwargs, self.args = {}, []

        def __getattr__(self, attr):
            if kwprops:
                for prop_name, prop_values in kwprops.items():
                    if attr in prop_values and prop_name not in self.kwargs:
                        self.kwargs[prop_name] = attr
                        return self
            elif attr in props:
                self.args.append(attr)
                return self
            raise AttributeError("%s parameter is duplicated or not allowed!" % attr)

        def __call__(self, *args, **kwargs):
            if kwprops:
                kwargs.update(self.kwargs)
                self.kwargs = {}
                return self.func(*args, **kwargs)
            else:
                new_args, self.args = self.args + list(args), []
                return self.func(*new_args, **kwargs)
    return Wrapper

class AdbClient(object):
    def __init__(self, serialno=None):
        subprocess.Popen(["adb", "start-server"], shell=True).wait()
        self.session = None
        if serialno:
            self.serialno = serialno
            state = self.get_device_state
            if state != "device":
                raise EnvironmentError("Device is %s." % state)
        else:
            self.serialno = self.device_serial(serialno)
    
    def device_serial(self, serialno=None):
        if not serialno:
            devices = self.get_serialnos()
            if devices:
                if len(devices) is 1:
                    serialno = list(devices.keys())[0]
                else:
                    raise EnvironmentError("Multiple devices attached but default android serial not set.")
            else:
                raise EnvironmentError("Device not attached.")
        return serialno

    @property
    def get_device_state(self):
        return self.adb_command(["get-state"]).strip()
       
    def get_serialnos(self):
        out = self.dos_command(["adb", "devices"], timeout=10)
        match = "List of devices attached"
        index = out.find(match)
        if index < 0:
            raise EnvironmentError("adb is not working.")
        return dict([s.split("\t") for s in out[index + len(match):].strip().splitlines() if s.strip().endswith("device")])
            
    def dos_command(self, cmd, timeout=5, kil=True):
        if isinstance(cmd, str):
            cmd = cmd.split()
        if not cmd:
            raise Exception
        p = psutil.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ""
        
        def readData(f, buff):
            data = f.readline().decode("utf-8")
            buff.append(data)
            
        while True:
            buff = []
            th = Thread(target=readData, args=(p.stdout, buff))
            th.setDaemon(True)
            th.start()
            th.join(timeout=timeout)
            if not buff or not buff[0]:
                if not kil:
                    return p
                if p.is_running():
                    try:
                        for c in p.children():
                            c.kill()
                        p.kill()
                    except Exception:
                        pass
                return output
            line = buff[0].strip()+"\n"
            del buff
            output += line
        
    
    def adb_command(self, cmd, timeout=5, kil=True):
        cmds = ['adb', '-s', self.serialno] if self.serialno else ['adb']
        if isinstance(cmd, str):
            cmd = cmd.split()
        cmds.extend(cmd)
        return self.dos_command(cmds, timeout=timeout, kil=kil)
    
    def takeSnapshot(self, filename):
        device_file = "/data/local/tmp/screenshot.png"
        self.adb_shell(["screencap", device_file])
        if os.path.isabs(filename):
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)            
        self.adb_command(["pull", device_file, filename])
        self.adb_shell(["rm", "-rf", device_file])
        return filename
    
    def adb_shell(self, cmd, timeout=5, kil=True):
        if isinstance(cmd, str):
            cmd = cmd.split()
        return self.adb_command(["shell"]+cmd, timeout=timeout, kil=kil)
    
    def forward(self, local, remote, rebind=True):
        if rebind:
            return self.adb_command(["forward", "tcp:%d"%local, "tcp:%d"%remote])
        return self.adb_command(["forward", "--no-rebind", "tcp:%d"%local, "tcp:%d"%remote])
    
    def input_text(self, text):
        if type(text) is str:
            escaped = text.replace('%s', '\\%s')
            encoded = escaped.replace(' ', '%s')
        else:
            encoded = str(text)
        self.adb_shell(["input", "text", "\"%s\"" % encoded])
    
    def input_tap(self, x, y):
        self.adb_shell(["input", "tap", "%d"%x, "%d"%y])
        
    def input_keyevent(self, keycode):
        self.adb_shell(["input", "keyevent", keycode])
    
    def input_swipe(self, x1, y1, x2, y2, duration=50):
        self.adb_shell(["input", "swipe", "%d"%x1, "%d"%y1, "%d"%x2, "%d"%y2, "%d"%duration])
        
    def forward_list(self):
        return self.adb_command(["forward", "--list"]).splitlines()
    
    def uninstall(self, pkgs):
        if isinstance(pkgs, str):
            pkgs = pkgs.split()
        for pkg in pkgs:
            self.adb_shell(["pm", "uninstall", pkg], timeout=20)
    
    def install(self, apks):
        if isinstance(apks, str):
            apks = apks.split()
        for apk in apks:
            self.adb_command(["install", "-r", "-t", apk], timeout=20)
    
    def get_data_connected_status(self):
        """get the status of data connection.
        @return: "True","False"
        """
      
        status = self.adb_shell(["ifconfig", "rmnet0"])
        returncode = re.search(r'rmnet0:\sip\s(?P<g1>.*)\smask.*\[up', status)
        return bool(returncode)
    
    def get_data_service_state(self):
        """get data service state to judge whether attach the operator network.
        @return: "2G","3G","LTE","UNKNOWN"
        """
        data = self.adb_shell(["dumpsys", "telephony.registry"])
        index = data.find("mServiceState")
        index2 = data.find("\n", index)
        assert index2 > -1
        data = data[index:index2-1].lower()
        if data.find("edge") > -1 or data.find ("gprs") > -1 or data.find("1xrtt") > -1 or data.find("gsm") > -1:
            return "2G"
        elif data.find("evdo") > -1 or data.find("hsupa") > -1 or data.find("hsdpa") > -1 or data.find("hspa") > -1:
            return "3G"
        elif data.find("lte") > -1:
            return "LTE"
        else:  
            return "UNKNOWN"  
         
    def get_call_state(self):
        """get call service state to judge whether attach the operator network.
        @return:  "idle","ringing","incall"
        """
         
        data = self.adb_shell(["dumpsys telephony.registry"]) 
        if data.find("mCallState=0") > -1:
            return "idle"
        elif data.find("mCallState=1") > -1:
            return  "ringing"
        elif data.find("mCallState=2") > -1:
            return  "incall"
        else: 
            return "UNKNOWN"
    
    def isKeyboardShown(self):
        '''
        Whether the keyboard is displayed.
        '''
        dim = self.adb_shell(['dumpsys', 'input_method'])
        if dim:
            return "mInputShown=true" in dim
        return False
    
    def getTopActivityNameAndPid(self):
        dat = self.adb_shell(['dumpsys', 'activity', 'top'])
        activityRE = re.compile('\s*ACTIVITY ([A-Za-z0-9_.]+)/([A-Za-z0-9_.]+) \w+ pid=(\d+)')
        m = activityRE.search(dat)
        if m:
            return (m.group(1), m.group(2), m.group(3))
        return None
        
    def isScreenOn(self):
        '''
        Checks if the screen is ON.

        @return True if the device screen is ON
        '''
        screenOnRE = re.compile('mScreenOnFully=(true|false)')
        m = screenOnRE.search(self.adb_shell(['dumpsys', 'window', 'policy']))
        if m:
            return (m.group(1) == 'true')
    
    def isLocked(self):
        '''
        Checks if the device screen is locked.

        @return True if the device screen is locked
        '''
        lockScreenRE = re.compile('Lockscreen=(true|false)')
        m = lockScreenRE.search(self.adb_shell(['dumpsys', 'window', 'policy']))
        if m:
            return (m.group(1) == 'true')
        
    def get_incomingcall_number(self):
        """get call service state to judge whether attach the operator network.
        @return:  "None",imcoming/outgoing call number,"UNKNOWN"
        """
         
        data = self.adb_shell(["dumpsys", "telephony.registry"])
        index = data.find("mCallState")
        index2 = data.find("\n", index)
        assert index2 > -1  
        data1 = data[index:index2-1].lower()
        index3 = data.find("mCallIncomingNumber")
        index4 = data.find("\n", index3)
        assert index4 > -1  
        data2 = data[index3+20:index4-1].lower()             
        if data1.find("1") > -1:
            return  data2 
        elif data1.find("2") > -1:
            return  data2                 
        else:
            return "UNKNOWN" 
        
    def get_meminfo(self):
        '''get memory info'''
        return self.adb_shell(["dumpsys", "meminfo"])
    
    def get_cpuinfo(self):
        '''get cpu info'''
        return self.adb_shell(["dumpsys", "cpuinfo"])
    
    def shell_adb(self, cmd):
        return self.adb_command(cmd)
    
    def start_activity(self, *argv):
        cmd = ['am', 'start', "-n"]
        if argv:
            if len(argv)==2:
                argv=argv[0]+"/"+argv[1],
            cmd.append(*argv)
        self.adb_shell(cmd, timeout=5)
    
    def launch_app(self, package):
        self.adb_shell(["monkey", "-p", package, "1"], timeout=5)
    
    def adaptRotation(self, coord, size, rotation=0):
        if rotation == 0:
            return coord
        elif rotation == 90:
            height, width = size
            x_coord, y_coord = coord
            x = y_coord
            y = width - x_coord
            return (x, y)
        elif rotation == 180:
            height, width = size
            x_coord, y_coord = coord
            x = x_coord
            y = y_coord
            return (x, y)
        elif rotation == 270:
            height, width = size
            x_coord, y_coord = coord
            x = height - y_coord
            y = x_coord
            return (x, y)
        else:
            return None

    def getMatchedCenterOffset(self, subPath, srcPath, threshold=0.03, rotation=0):
        '''
        get the coordinate of the mathced sub image center point.
        @type subPath: string
        @params subPath: the path of searched template. It must be not greater than the source image and have the same data type.
        @type srcPath: string
        @params srcPath: the path of the source image where the search is running.
        @type threshold: float
        @params threshold: the minixum value which used to increase or decrease the matching threshold. 0.01 means at most 1% difference.
                       default is 0.01.
        @type rotation: int
        @params rotation: the degree of rotation. default is closewise. must be oone of 0, 90, 180, 270
        @rtype: tuple
        @return: (x, y) the coordniate tuple of the matched sub image center point. return None if sub image not found or any exception.
        '''
        for img in [subPath, srcPath]: assert os.path.exists(img) , "No such image:  %s" % (img)
        if hasattr(cv2, "cv"):
            method = cv2.cv.CV_TM_SQDIFF_NORMED #Parameter specifying the comparison method
        else:
            method = cv2.TM_SQDIFF_NORMED 
        try:
            subImg = cv2.imread(subPath) #Load the sub image
            srcImg = cv2.imread(srcPath) #Load the src image
            result = cv2.matchTemplate(subImg, srcImg, method) #comparision, 越小的数值代表更高的匹配结果
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result) #Get the minimum squared difference,minMaxLoc寻找矩阵(一维数组当作向�?用Mat定义) 中最小值和最大值的位置.
            del maxVal
            del maxLoc
            if minVal <= threshold:
                minLocXPoint, minLocYPoint = minLoc
                subImgRow, subImgColumn = subImg.shape[:2]
                centerPoint = (minLocXPoint + int(subImgRow/2), minLocYPoint + int(subImgColumn/2))
                (height, width) = srcImg.shape[:2]

                return self.adaptRotation(coord=centerPoint, size=(height, width), rotation=rotation)
            else:
                return None    
        except:
            return None
        
    def click_image(self, imagename, waittime=1, threshold=0.01, rotation=0):
        '''
            click  the subPath image exists in the current screen.
            @type imagename: string
            @params imagename: the name  of searched imagename.  
            @type waittime: int
            @params waittime:Delay execution for a given number of seconds after click.  
            @type threshold: float
            @params threshold: the minixum value which used to increase or decrease the matching threshold. 0.01 means at most 1% difference. default is 0.01. 
            @type rotation: int
            @params rotation: the degree of rotation. default is closewise. must be oone of 0, 90, 180, 270  
            @rtype: boolean
            @return: true if the sub image founded in the src image. return false if sub image not found or any exception.
        '''
        '''
        if the wanted image found on current screen click it.
        if the wanted image not found raise exception and set test to be failure.
        '''
        expect_image_path = None
        current_image_path = None
        report_dir_path = os.path.join(os.getcwd(), "tmp")
        right_dir_path = os.getcwd()
        if os.path.isabs(imagename):
            expect_image_path = imagename
            report_dir_path = os.path.split(imagename)
            current_image_path = os.path.join(report_dir_path[0],"tmp", report_dir_path[1])
        else:
            expect_image_path = os.path.join(right_dir_path, imagename)
            current_image_path = os.path.join(report_dir_path, imagename)       

        if not os.path.exists(expect_image_path):
            return False

        self.takeSnapshot(current_image_path)#====================== 
        if not os.path.exists(current_image_path):
            return False
        pos = self.getMatchedCenterOffset(subPath=expect_image_path, srcPath=current_image_path, threshold=0.03, rotation=rotation)
        if not pos:
            return False
        self.input_tap(*pos)
        self.delay(waittime)
        return pos
    
    def isMatch(self, subPath, srcPath, threshold=0.03):
        '''
        check wether the subPath image exists in the srcPath image.
        @type subPath: string
        @params subPath: the path of searched template. It must be not greater than the source image and have the same data type.
        @type srcPath: string
        @params srcPath: the path of the source image where the search is running.
        @type threshold: float
        @params threshold: the minixum value which used to increase or decrease the matching threshold. 0.01 means at most 1% difference. default is 0.01. 
        @rtype: boolean
        @return: true if the sub image founded in the src image. return false if sub image not found or any exception.
        '''
        for img in [subPath, srcPath]: assert os.path.exists(img) , 'No such image:  %s' % (img)
        if hasattr(cv2, "cv"):
            method = cv2.cv.CV_TM_SQDIFF_NORMED #Parameter specifying the comparison method
        else:
            method = cv2.TM_SQDIFF_NORMED 
        try:
            subImg = cv2.imread(subPath) #Load the sub image
            srcImg = cv2.imread(srcPath) #Load the src image
            result = cv2.matchTemplate(subImg, srcImg, method) #comparision
            minVal = cv2.minMaxLoc(result)[0] #Get the minimum squared difference
            if minVal <= threshold: #Compared with the expected similarity
                return True
            else:
                return False
        except:
            return False
            
    def find(self, imagename, interval=2, timeout=4, threshold=0.01):
        
        '''
            check wether the  image exists in the current scrren in a interval search time within a timeout.
            @type imagename: string
            @params imagename: the name  of searched imagename. 
            @type interval: int
            @params interval: the interval to search the image within the timeout.
            @type timeout: int
            @params timeout: the timeout to search the image. 
             @type threshold: float
            @params threshold: the minixum value which used to increase or decrease the matching threshold. 0.01 means at most 1% difference. default is 0.01. 
            @rtype: boolean
            @return: true if the sub image founded in the src image. return false if sub image not found or any exception.
        '''
        '''
        if the expected image found on current screen return true else return false
        '''
        expect_image_path = None
        current_image_path = None
        right_dir_path = os.getcwd()
        report_dir_path = os.path.join(right_dir_path, "tmp")        
        if os.path.isabs(imagename):
            right_dir_path
        else:
            expect_image_path = os.path.join(right_dir_path, imagename)
            current_image_path = os.path.join(report_dir_path, imagename)

        if not os.path.exists(expect_image_path):
            return False
        begin = time.time()        
        while (time.time() - begin < timeout):            
            self.takeSnapshot(current_image_path)
            if self.isMatch(expect_image_path , current_image_path , threshold):
                return True
            self.delay(interval)
        return False
    
    def delay(self, seconds=1):
        time.sleep(seconds)
        
if __name__ == "__main__":
    adb = AdbClient()
    print(adb.isLocked())

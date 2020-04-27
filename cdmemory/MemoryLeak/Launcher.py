import unittest, traceback, time
from lib.PSSValue import SampleAndReport
from lib import common
from lib.getconfigs import GetConfigs
from lib.launcher import Launcher
from lib.fileManager import FileManager

logger = common.createlogger("MAIN")
logger.debug("Connect devices")
mdevice = common.connect_device("MDEVICE")
# mdevice = common.connect_device("GAWKFQT8WGL7L7S8")
mLauncher = Launcher(mdevice, "M_LAUNCHER")
mFileManager = FileManager(mdevice,'M_FILEMANAGER')

cfg = GetConfigs("Launcher")
test_times = cfg.get_test_times()
logger.info("Trace Total Times " + str(test_times))


class LauncherCases(unittest.TestCase):
    pids = ["com.tcl.android.launcher"]
    def setUp(self):
        mLauncher.clearLauncher()
        self._name = "Launcher_case" + self._testMethodName + "_" + mLauncher.GetNowTime()
        self.sr = SampleAndReport(self.pids, sample=3, 
                                  caseName = self._name,
                                  device = common.get_deviceId("MDEVICE"))
        self.sr.start()

        
    def tearDown(self):
        mLauncher.backToHome()
        self.sr.stop()
        
    def testSetWallpaper(self):        
        logger.info("test set wallpaper with big picture")
        startTime = time.time()
        logger.info("Set wallpaper")
        loop = 0
        while time.time() - startTime < test_times:            
            if mLauncher.setWallpaper(loop+1):                
                logger.info('Trace Success Loop')
            else:
                logger.warning('Set wallpaper with big picture fail')
                mLauncher.save_fail_img()
            loop += 1
        
    def testCreateFolder(self):
        logger.info("test create folder on home screen")
        startTime = time.time()
        logger.info('Create Folder')
        while time.time() - startTime < test_times:
            try:
                if mLauncher.createFolder() and mLauncher.deleteFolder():
                    logger.info('Trace Success Loop')
                else:
                    logger.warning("create folder on home screen fail!")
                    mLauncher.save_fail_img()
            except Exception:
                logger.warning('Create Folder Exception')
                common.log_traceback(traceback.format_exc())
                mLauncher.save_fail_img()
                mLauncher.backToHome()
                   
    def testOpenCloseFolder(self):        
        logger.info("test open and close folder on home screen")
        startTime = time.time()
        logger.info('Open and Close Folder')
        mLauncher.createFolder()
        while time.time() - startTime < test_times:
            try:
                if mLauncher.openFolder() and mLauncher.closeFolder():
                    logger.info('Trace Success Loop ')
                else:
                    logger.warning('Open and Close Folder Fail')   
                    mLauncher.save_fail_img()                
            except Exception:
                logger.warning('Open and Close Folder Exception')
                common.log_traceback(traceback.format_exc())
                mLauncher.save_fail_img()
                mLauncher.backToHome()  
        mLauncher.deleteFolder()
                
    def testCreateShortcut(self):
        logger.info('test create shortcut on home screen')
        startTime = time.time()
        logger.info('Create Shortcut')
        while time.time() - startTime < test_times:
            try:
                if mLauncher.addShortcut(5):#5
                    logger.info('Trace Success Loop')
                else:
                    logger.warning('Create Shortcut Fail')   
                    mLauncher.save_fail_img() 
                mLauncher.clearLauncher()
            except Exception:
                common.log_traceback(traceback.format_exc())
                mLauncher.save_fail_img()
                mLauncher.backToHome()
               
    def testChangeIdle(self):
        logger.info('test change idle screen')
        startTime = time.time()
        mLauncher.prepareIdle()
        logger.info('Change Idle')
        while time.time() - startTime < test_times:
            try:
                if mLauncher.changeIdle():
                    logger.info('Trace Success Loop')                    
            except Exception:
                common.log_traceback(traceback.format_exc())
                mLauncher.save_fail_img()
                mLauncher.backToHome()
                
    def testAddDelDynamicAPP(self):
        logger.info('test add dynamic app to home screen')
        apps=['Calendar']
        startTime = time.time() 
        logger.info('Add Dynamic APP')    
        while time.time() - startTime < test_times:
            try:
                if mLauncher.addDynamicApp(apps[0]):
                    mLauncher.removeApp(apps[0])
                    logger.info('Trace Success Loop')
                else:
                    logger.warning('Add Dynamic App Fail')
                    mLauncher.save_fail_img()   
            except Exception:
                common.log_traceback(traceback.format_exc())
                mLauncher.save_fail_img()
                mLauncher.backToHome()
                    
    def testAddWidget(self):
        logger.info('test add widget on home screen')
        startTime = time.time()
        logger.info('Add Widget')
        while time.time() - startTime < test_times:
            try:
                if mLauncher.addWidget(5):
                    logger.info('Trace Success Loop')
                else:
                    logger.warning('Add Widget Fail')
                    mLauncher.save_fail_img()
                mLauncher.clearAllShortcut()                       
            except Exception:
                common.log_traceback(traceback.format_exc())
                mLauncher.save_fail_img()
                mLauncher.backToHome()
                    
    def testInstallAPK(self):
        logger.info('test Install APK')
        startTime = time.time()
        logger.info('Install APK, %s times')   
        while time.time() - startTime < test_times:
            try:
#                 mFileManager.enterFolder()
                if mLauncher.installAPK():
                    logger.info('Trace Success Loop')
                else:
                    logger.warning('Install APK Fail')
                    mLauncher.save_fail_img()                        
                mLauncher.backToHome()
                mLauncher.uninstallAPK()
            except Exception:
                common.log_traceback(traceback.format_exc())
                mLauncher.save_fail_img()
                mLauncher.backToHome()

if __name__ == "__main__":
    common.runTest(LauncherCases, [
                                    # "testSetWallpaper",
                                    # "testCreateFolder",
                                    # "testOpenCloseFolder",
                                    "testCreateShortcut",
                                    # "testChangeIdle",
                                    # "testAddDelDynamicAPP",
                                    # "testAddWidget",
                                    # "testInstallAPK"
                                   ])


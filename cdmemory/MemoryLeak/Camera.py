import unittest, traceback
from lib.PSSValue import SampleAndReport
import  time
from lib import common
from lib.common import Common
from lib.getconfigs import GetConfigs
from lib.camera import Camera
logger = common.createlogger("MAIN")
logger.debug("Connect devices")
mdevice = common.connect_device("MDEVICE")
# mdevice = common.connect_device("GAWKFQT8WGL7L7S8")
mCam = Camera(mdevice, "Camera")
path = mCam.get_SDcard_name()

cfg = GetConfigs("Camera")
test_times = cfg.get_test_times()
logger.info("Trace Total seconds " + str(test_times))

class CameraCases(unittest.TestCase):
    pids = ["com.tcl.camera", "mediaserver"]
    def setUp(self):
        mCam.backToHome()
        mdevice.shell_adb("shell rm -rf /sdcard/"+path+"/DCIM/Camera/*")
        mdevice.delay(2)
        # mdevice.shell_adb("shell pm clear com.tcl.camera")
        self._name ="Camera_case_" + self._testMethodName+"_"+mCam.GetNowTime()
        self.sr = SampleAndReport(self.pids, sample=3, 
                                  caseName = self._name, 
                                  device = common.get_deviceId("MDEVICE"))               
        self.sr.start()        
        
    def tearDown(self):        
        mCam.backToHome()
        self.sr.stop()
        for pid in self.pids:
            mCam.saveMeminfo(type = "End", 
                             packageName = pid, 
                             filename = self._name) 
        
    def testCaputurePictures(self):
        logger.info("Capture pictures")
        startTime = time.time()
        if mCam.enter_camera():            
            while time.time() - startTime < test_times:
                try:                    
                    if mCam.take_photo("back"):
                        logger.info("Trace Success Loop")
                    else:
                        logger.warning("Camera test fail!")
                        mCam.save_fail_img()
                except Exception:
                    mCam.save_fail_img()
                    logger.warning("Camera test Exception!")
                    common.log_traceback(traceback.format_exc())
                    mCam.backToHome()
                    mCam.enter_camera()
                    
    def testCaptureVideos(self):
        startTime = time.time()
        logger.info("Capture video")
        if mCam.enter_camera():
            while time.time() - startTime < test_times:
                try:                    
                    if mCam.takeVideo("back"):
                        logger.info("Trace Success Loop")
                    else:
                        logger.warning("Video test fail!")
                        mCam.save_fail_img()
                except Exception:
                    mCam.save_fail_img()
                    logger.warning("Video test Exception!")
                    common.log_traceback(traceback.format_exc())
                    mCam.backToHome()
                    mCam.enter_camera()
                    
    def testSwitchCamera(self):
        startTime = time.time()
        logger.info("switch camera")
        if mCam.enter_camera():
            while time.time() - startTime < test_times:
                try:                    
                    if mCam.take_photo("front") and mCam.take_photo("back"):
                        logger.info("Trace Success Loop ")
                    else:
                        logger.warning("Camera test fail!")
                        mCam.save_fail_img()
                except Exception:
                    mCam.save_fail_img()
                    logger.warning("Camera test Exception!")
                    common.log_traceback(traceback.format_exc())
                    mCam.backToHome()
                    mCam.enter_camera()
                    
    def testSwitchScenario(self):        
        startTime = time.time()
        logger.info("Switch Scenario")
        
        if mCam.enter_camera():
            while time.time() - startTime < test_times:
                try:
                    scenarios = ['AUTO','PORTRAIT','WIDE']
                    for scenario in scenarios:
                        if mCam.switchScenario(scenario):                            
                            logger.info("Trace Success Loop")
                        else:
                            logger.warning("Camera test fail!")
                            mCam.save_fail_img()
                except Exception:
                    mCam.save_fail_img()
                    logger.warning("Camera test Exception!")
                    common.log_traceback(traceback.format_exc())
                    mCam.backToHome()
                    mCam.enter_camera()
                    
    def testReEnterCamera(self):
        startTime = time.time()
        logger.info("ReEnter Camera")  
        while time.time() - startTime < test_times:
            try:  
                if mCam.reEnterCamera():
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("Camera test fail!")
            except Exception:
                mCam.save_fail_img()
                logger.warning("Camera test Exception!")
                common.log_traceback(traceback.format_exc())
                mCam.backToHome()
                mCam.enter_camera()
    
    def testEnterCameraByRecent(self):                
        startTime = time.time()        
        logger.info("ReEnter Camera")  
        mCam.clearAllRecent()
        while time.time() - startTime < test_times:
            try:  
                if mCam.enterCameraByRecent():
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("Camera test fail!")
                mCam.backToHome()
            except Exception:
                mCam.save_fail_img()
                logger.warning("Camera test Exception!")
                common.log_traceback(traceback.format_exc())
                mCam.backToHome()
                mCam.enter_camera()
                
    def testBurstShot(self):                
        startTime = time.time()  
        logger.info("Burst Shot")
        if mCam.enter_camera():
            while time.time() - startTime < test_times:
                try:
                    if mCam.burstShot():
                        logger.info("Trace Success Loop")
                    else:
                        logger.warning("Camera test fail!")
                        mCam.save_fail_img()
                except Exception:
                    mCam.save_fail_img()
                    logger.warning("Camera test Exception!")
                    common.log_traceback(traceback.format_exc())
                    mCam.backToHome()
                    mCam.enter_camera()
                
if __name__ == "__main__":    
    common.runTest(CameraCases, [
                                "testCaputurePictures",
                                "testCaptureVideos",
                                "testSwitchCamera",
                                "testSwitchScenario",
                                "testReEnterCamera",
                                "testEnterCameraByRecent",
                                "testBurstShot"
                                  ])

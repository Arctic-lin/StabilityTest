import unittest, traceback
from lib.PSSValue import SampleAndReport
import time
from lib import common
from lib.getconfigs import GetConfigs
from lib.messageModule import Message

logger = common.createlogger("MAIN")
logger.debug("Connect devices")
mdevice = common.connect_device("MDEVICE")
mdevice = common.connect_device("GAWKFQT8WGL7L7S8")
mMsg =  Message(mdevice, "Message")

cfg = GetConfigs("Message+")
test_times = cfg.get_test_times()
logger.info("Trace Total Times " + str(test_times))


class MessageTestCase(unittest.TestCase):   
    pids = ["com.google.android.apps.messaging"] 
    
    def setUp(self):
        mMsg.backToHome()
        mMsg.clearAllRecent()
        mMsg.enter_message()
        #mdevice.shell_adb("shell pm clear com.vodafone.messaging")
        self._name = "Message+_case_" + self._testMethodName + "_" + mMsg.GetNowTime()
        self.sr = SampleAndReport(self.pids, sample=3,
                                  caseName = self._name,
                                  device = common.get_deviceId("MDEVICE"))
        self.sr.start()
        
    def tearDown(self):
        mMsg.backToHome()
        self.sr.stop() 
        for pid in self.pids:
            mMsg.saveMeminfo(type = "End", 
                             packageName = pid, 
                             filename = self._name) 
       
    def testNewAndCloseSMS(self):
        startTime = time.time()
        logger.info("NewAndCloseSMS")
        while time.time() - startTime < test_times:
            try:
                if mMsg.newAndSendMessage():                
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("testNewAndCloseSMS test failed.")
            except Exception:
                mMsg.save_fail_img()
                logger.warning("testNewAndCloseSMS Exception!")
                common.log_traceback(traceback.format_exc())
                mMsg.backToHome()
    
    def testEnterCamera(self):
        startTime = time.time()
        logger.info("EnterCamera")
        while time.time() - startTime < test_times:
            try:
                if mMsg.takeFromMessage("Photo") and mMsg.takeFromMessage("Video"):
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("testEnterCamera test failed.")
            except Exception:
                mMsg.save_fail_img()
                logger.warning("testEnterCamera Exception!")
                common.log_traceback(traceback.format_exc())
                mMsg.backToHome()
    
    def testEnterGallery(self):
        startTime = time.time()
        logger.info("EnterPhotos")
        while time.time() - startTime < test_times:
            try:
                if mMsg.enterGalleryfromMessage():
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("testEnterGallery test failed.")
            except Exception:
                mMsg.save_fail_img()
                logger.warning("testEnterGallery Exception!")
                common.log_traceback(traceback.format_exc())
                mMsg.backToHome()        
        
    
    def testSlideAndPreviewMedia(self):
        startTime = time.time()
        logger.info("SlideAndPreviewMedia")
        while time.time() - startTime < test_times:
            try:
                if mMsg.slideAndPreviewMedia(mediaType = "image") and mMsg.slideAndPreviewMedia(mediaType = "video"):
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("testSlideAndPreviewMedia test failed.")
            except Exception:
                mMsg.save_fail_img()
                logger.warning("testSlideAndPreviewMedia Exception!")
                common.log_traceback(traceback.format_exc())
                mMsg.backToHome()
    
    def testAddSoundRecord(self):
        startTime = time.time()
        logger.info("AddSoundRecord ")
        while time.time() - startTime < test_times:
            try:
                if mMsg.takeFromMessage("Audio"):
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("testAddSoundRecord test failed.")
            except Exception:
                mMsg.save_fail_img()
                logger.warning("testAddSoundRecord Exception!")
                common.log_traceback(traceback.format_exc())
                mMsg.backToHome()
    
    def testAddAndDeleteAttachment(self):
        startTime = time.time()
        logger.info("addAndDeleteAttachment")
        while time.time() - startTime < test_times:       
            try:
                if mMsg.addAndDeleteAttachment():
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("addAndDeleteAttachment test failed.")
            except Exception:
                mMsg.save_fail_img()
                logger.warning("addAndDeleteAttachment Exception!")
                common.log_traceback(traceback.format_exc())
                mMsg.backToHome()
    
    def testShareInfoAndDelete(self):
        startTime = time.time()
        logger.info("ShareInfoAndDelete")
        while time.time() - startTime < test_times:      
            try:
                if mMsg.sharePicAndVideo():
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("testShareInfoAndDelete test failed.")
            except Exception:
                mMsg.save_fail_img()
                logger.warning("testShareInfoAndDelete Exception!")
                common.log_traceback(traceback.format_exc())
                mMsg.backToHome()            
    
    def testSlideToReadInfo(self):
        startTime = time.time()
        logger.info("SlideToReadInfo")
        if not mMsg.enter_message():
            mMsg.enter_message() 
        # mMsg._device(resourceId="android:id/list").child(index=0).click.wait()
        if mMsg._device (text="181 3688 7453").exists:
            mMsg._device (text="181 3688 7453").click.wait()
        mMsg._device.delay(1)
        while time.time() - startTime < test_times:
            try:
                for _ in range(5):
                    mMsg._device.swipe(360,200,360,1080,10)
                    mMsg._device.delay(1)
                for _ in range(5):
                    mMsg._device.swipe(360,1080,360,200,10)
                    mMsg._device.delay(1)
                logger.info("Trace Success Loop")
            except Exception:
                mMsg.save_fail_img()
                logger.warning("testSlideToReadInfo Exception!")
                common.log_traceback(traceback.format_exc())
                mMsg.backToHome()


if __name__ == "__main__":
    common.runTest(MessageTestCase, [
                                    "testSlideToReadInfo",
                                    "testNewAndCloseSMS",
                                    "testEnterCamera",
                                    "testEnterGallery",
                                    "testSlideAndPreviewMedia",
                                    "testAddSoundRecord",
                                    "testAddAndDeleteAttachment",
                                    "testShareInfoAndDelete",
                                    ])

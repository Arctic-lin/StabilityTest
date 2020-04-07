# -*- coding: UTF-8 -*-
import common, traceback
from common import Common
email_package = 'com.tcl.email'
email_activity = 'com.tct.email.activity.Welcome'

class Email(Common):
    """Provide common functions involved email."""    
    def __init__(self, device, log_name="EMAIL"):
        Common.__init__(self, device,log_name)
    
    def enter_email(self):
        self._logger.debug("Launch email.")
        self._device.start_activity(email_package, email_activity)
        self._device.delay(3)
        if self._device.currentPackageName == email_package:
            self._logger.debug('Launch email successful')
            return True
        self._logger.debug('Launch email fail')
        return False
    
    def setInboxEmailRead(self):
        self.enter_email()
        self.enter_mailbox("Inbox")
        if self._device(resourceId="com.tct.email:id/dismiss_button").exists:
            self._device(resourceId="com.tct.email:id/dismiss_button").click()
            self._device.delay(1)
        for _index in range(2):
            self._device(className='android.widget.ListView').child(className='android.view.View', instance=_index).click.wait()
            self._device.delay(1)
            self._device.press("back")
            self._device.delay(1)
    
    def getCurrentBoxName(self):
        navItem = self._device(description='Open navigation drawer')
        if not navItem.exists:
            self._device.press("back")
            self._device.delay(1)
        return navItem.sibling(className="android.widget.TextView").getText()
        
    def enter_mailbox(self, box):
        if self._device(resourceId="com.tct.email:id/dismiss_button").exists:
            self._device(resourceId="com.tct.email:id/dismiss_button").click()
            self._device.delay(1)
        if self.getCurrentBoxName() == box:
            return True
        self._device(description='Open navigation drawer').click.wait()
        self._device.delay(1) 
        self._device(resourceId='com.tcl.email:id/name', text=box).click.wait()
        self._device.delay(1)  
        if self.getCurrentBoxName() == box:
            if not self._device(resourceId='com.tcl.email:id/loading_progress').wait.gone(timeout=10000):
                self.refreshBox()
            return True
        self._logger.debug('enter %s fail!', box)
        return False
            
    def forward_email(self, _index, address, body="fyi"):
        self.enter_mailbox("Inbox")
        if self._device(description='Dismiss tip').exists:
            self._device(description='Dismiss tip').click()
            self._device.delay(1)
        self._logger.debug('select an email')
        self._device(className='android.widget.ListView').child(className='android.view.View', instance=_index).click()
        self._device.delay(2)
        self._device(resourceId="com.tcl.email:id/overflow").click()
        self._device.delay(1)
        self._device(text='Forward').click()
        self._device.delay(1)
        okBtn = self._device(text="OK")
        if okBtn.exists:
            okBtn.click()
        self._device(className='android.widget.MultiAutoCompleteTextView', description='To').set_text(address+"; ")
        self._device.delay(1)
        self._device(resourceId="com.tcl.email:id/body").set_text(body)
        self._device.delay(1)
        return self.isEmailSent()
        
    
    def getEmailNum(self):
        if self._device(resourceId="com.tcl.email:id/empty_icon").exists:
            return 0
        return self._device(className="android.view.View").count-2
    
    def delMailbox(self, box):
        if self.enter_mailbox(box):
            for _ in range(1000):
                try:
                    if not self._device(resourceId='com.tcl.email:id/loading_progress').wait.gone(timeout=10000):
                        self.refreshBox()
                        continue
                    if self.getEmailNum() == 0:
                        return True
                    if self.getCurrentBoxName() == "Inbox" and self.getEmailNum() <= 2:
                        return True
                    if self.getCurrentBoxName() == "Trash" and self._device(text="Empty Trash").exists:
                        self._device(text="Empty Trash").click()
                        self._device.delay(2)
                        self._device(text="Delete").click()
                        self._device(resourceId="com.tcl.email:id/empty_icon").wait.exists(timeout=20000)
                        continue
                    if box == "Outbox":
                        #self._device.long_click(360,300)
                        self._device(className='android.widget.ListView').child(className='android.view.View', instance=0).long_click()
                        self._device.delay(1)
                        discardBtn = self._device(description = 'More options')
                        if discardBtn.exists:
                            discardBtn.click()
                            self._device.delay(1)
                            self._device(text = "Discard").click()
                            self._device.delay(2)
                            self.backToEmailList()
                            return True
                    self._device(className='android.widget.ListView').child(className='android.view.View', instance=0).click()
                    self._device.delay(2)
                    if box == "Drafts":
                        delBtn = self._device(resourceId="com.tcl.email:id/discard_drafts")
                    else:
                        delBtn = self._device(resourceId="com.tcl.email:id/delete")
                    if delBtn.exists:
                        delBtn.click()
                        self._device.delay(1)
                    okBtn = self._device(text="OK")
                    if okBtn.exists:
                        okBtn.click()
                        self._device.delay(2)
                    self.backToEmailList()
                except Exception:
                    self.save_fail_img()
                    common.log_traceback(traceback.format_exc())
            return False
    
    def clearAllEmail(self, boxs=["Unread", "Drafts", "Outbox", "Sent", "Trash"]):
        self._logger.info("Clear boxes: "+", ".join(boxs))
        for box in boxs:
            self.delMailbox(box)
        self.backToEmailList()
    
    def isEmailSent(self):
        self._device(description='Send').click()
        self._device.delay(2)
        self._logger.debug('email sending...')
        self.backToEmailList()
        if self.enter_mailbox("Outbox"):
            for _ in range(9):
                if not self._device(resourceId="com.tcl.email:id/empty_icon").wait.exists(timeout=20000):
                    self.refreshBox()
                else:
                    break
            else:
                self._logger.debug('Email send fail in 3 minutes!!!')
                return False
        if self.enter_mailbox("Sent"):
            if self._device(resourceId="com.tcl.email:id/empty_icon").wait.gone(timeout=5000):
                self._logger.debug('email send success!!!')
                return True
        self._logger.debug('email send fail!!!')
        return False
     
    def reply_email(self, body="Auto test"):
        self._logger.debug("Reply email")
        import random
        Index=random.choice(range(1,5))
        self.enter_mailbox("Inbox")
        self._device(className='android.widget.ListView').child(className='android.view.View', instance=Index).click()
        self._device.delay(2)
        self._device(resourceId="com.tcl.email:id/overflow").click()
        self._device.delay(1)
        self._device(text='Reply').click.wait()
        self._device.delay(2)
        self._device(resourceId="com.tcl.email:id/body").set_text(body)
        self._device.delay(1)       
        return self.isEmailSent()
    
    def download_attachment(self):
        self._logger.debug('download attachment')
        self.enter_mailbox("Inbox")
        self._device(className='android.widget.ListView').child(className='android.view.View', instance=0).click()
        self._device.delay(3)
        download_item = self._device(resourceId='com.tcl.email:id/attachment_download_icon')
        if download_item.exists:
            download_item.click()
            self._device.delay(2)
            if self._device(resourceId='com.tcl.email:id/attachment_progress').wait.gone(timeout=120000):
                return True
        else:
            if self._device(resourceId='com.tcl.email:id/overflow',index=1).exists:
                self._device(resourceId='com.tcl.email:id/overflow',index=1).click()
                self._device.delay(1)
                self._device(text='Download again').click()
                self._device.delay(2)
                if self._device(resourceId='com.tcl.email:id/attachment_progress').wait.gone(timeout=120000):
                    return True
        return False
        
        
    def swipeToNextEmail(self):
        self._logger.debug('Swipe to the next email')
        w = self._device.displayWidth
        h = self._device.displayHeight
        self._device.swipe(w-100,h/2,w-650,h/2,steps=5)
        self._device.delay(2)
        return True
        
    def swipeToPreEmail(self):
        self._logger.debug('Swipe to the previous email')
        w = self._device.displayWidth
        h = self._device.displayHeight
        self._device.swipe(w-650,h/2,w-100,h/2,steps=5)
        self._device.delay(2)
        return True
        
    def swipeEmail(self):
        self._logger.debug('Swipe to next email and previous email')
        self.enter_mailbox("Inbox")
        self._device(className='android.widget.ListView').child(className='android.view.View', instance=0).click()
        self._device.delay(3)
        subjectText = self._device(resourceId='com.tcl.email:id/subject_and_folder_view').getText()
        for _ in range(50):
            self.swipeToNextEmail()
        for _ in range(50):
            self.swipeToPreEmail()
        if subjectText == self._device(resourceId='com.tcl.email:id/subject_and_folder_view').getText():
            return True
        return False
    
    def readEmail(self):
        self._logger.debug('open an email')
        self.enter_mailbox("Inbox")
        self._device(className='android.widget.ListView').child(className='android.view.View', instance=0).click()
        self._device.delay(3)
    
    def setOrientation(self,ori='natural'):
        self._logger.info('Set orientation to: '+ori)
        self._device.orientation = ori
        self._device.delay(0.5)
        return True
        
    def cancelSend(self, sendMethod='Reply'):
        self._logger.debug('cancel '+ sendMethod+' email')
        self.enter_mailbox("Inbox")
        self._device(className='android.widget.ListView').child(className='android.view.View', instance=0).click()
        self._device.delay(3)
        self._device(resourceId='com.tcl.email:id/overflow',description='More options').click.wait(timeout=3000)
        self._device.delay(1)
        self._device(text=sendMethod).click.wait(timeout=3000)
        self._device.delay(1)
        if self._device.isKeyboardShown():
            self._device.press('back')
        self._device.delay(1)
        self._device.press('back') 
        self._device.delay(1) 
        return self._device(resourceId='com.tcl.email:id/overflow',description='More options').exists
    
    def backToEmailList(self):
        for _ in range(5):
            if self._device(description='Open navigation drawer').exists:
                break
            self._device.press("back")
            self._device.delay(1)
    
    def saveAndSend(self, address, subject="Subject", body="Auto Test"):
        self._logger.debug("Save and send email")
        self._device(resourceId="com.tcl.email:id/compose_button").click()
        self._device.delay(2)
        self._device(resourceId="com.tcl.email:id/to").set_text(address+"; ")
        self._device.delay(1)
        self._device(resourceId="com.tcl.email:id/subject").set_text(subject)
        self._device.delay(1)
        self._device(resourceId="com.tcl.email:id/body").set_text(body)
        self._device.delay(1)
        self._device(description="More options").click()
        self._device.delay(2)
        self._device(text="Save draft").click()
        self._device.delay(1)
        self.backToEmailList()
        self.enter_mailbox("Drafts")
        self._device(className='android.widget.ListView').child(className='android.view.View', instance=0).click.wait()
        self._device.delay(2)
        self._device(resourceId="com.tcl.email:id/edit_draft").click()
        self._device.delay(1)
        addr = self._device(resourceId="com.tcl.email:id/to").get_text()
        sub = self._device(resourceId="com.tcl.email:id/subject").get_text()
        bod = self._device(resourceId="com.tcl.email:id/body").get_text()
        self._device.delay(1)
        if addr.find(address)>-1 and subject == sub and bod.find(body)>-1:
            saveFlag=True
        else:
            saveFlag=False
        if saveFlag:
            return self.isEmailSent()
        return False        
    
    def refreshBox(self):
        if self._device(className="android.widget.ListView").exists:
            self._device(className="android.widget.ListView").swipe.down(steps=2)
            self._device.delay(1)
        else:
            w = self._device.displayWidth
            h = self._device.displayHeight
            for _ in range(2):         
                self._device.drag(w/2, h/2, w/2, h-100, 2)
                self._device.delay(0.2)
            self._device.delay(1)
    
if __name__ == "__main__":
    d = common.Device("286e2a33")
    e = Email(d)
    e.refreshBox()

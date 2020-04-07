import os
import sys
import time

from common import Common
import utils

lib_path = os.path.dirname(os.path.abspath(__file__))
if lib_path not in sys.path:
    sys.path.append(lib_path)


class SetupWiz(Common):
    def setup(self):
        self.device.wakeup()
        self.logger.info('beginning')
        el = self.device(text='Hi there')
        if not el.exists:
            el = self.device(resourceId='com.google.android.setupwizard:id/language_picker')
            el.click.wait()
            el = self.device(textContains='United States')
            el.click.wait()
        el = self.device(textMatches='start|START')
        el.click.wait()
        self.logger.info('check sim cards if exists')
        el = self.device(text='SIM cards')
        if el.exists:
            el = self.device(resourceId='com.android.settings:id/next_button')
            el.click.wait()
        self.logger.info('connect to network')
        el = self.device(text='Connect to mobile network')
        if el.exists:
            el = self.device(textMatches='skip|SKIP')
            el.click.wait()
        self.logger.info('setup as new')
        el = self.device(text='Set up as new')
        el.click.wait()
        self.logger.info('connect to wifi if not ')
        # not a typo origin string contains not utf8 character
        el = self.device(textStartsWith='Connect to Wi')
        if el.exists:
            # wait wifi scan
            time.sleep(10)
            # not a typo origin string contains not utf8 character
            el = self.device(textStartsWith='See all Wi')
            el.click.wait()
            time.sleep(10)
            el = self.device(resourceId='com.google.android.setupwizard:id/suw_recycler_view')
            el.scroll.vert.to(text='Auto-korea')
            el = self.device(text='Auto-korea')
            el.click()
            el = self.device(resourceId='com.android.settings:id/password')
            el.set_text('Performance32')
            el = self.device(textMatches='connect|CONNECT')
            el.click()
        self.logger.info('wifi connect wait check for updates')
        self.device.delay(20)
        self.logger.info('wait checking for updates gone')
        el = self.device(textStartsWith='Checking for updates')
        el.wait.gone(timeout=120000)
        self.logger.info('wait checking info gone')
        el = self.device(textStartsWith='Checking info')
        el.wait.gone(timeout=120000)
        self.logger.info('login google account')
        el = self.device(resourceId='identifierId')
        el.set_text('perteam003@gmail.com')
        el = self.device(text='Next')
        el.click.wait()
        self.logger.info('wait account check')
        time.sleep(10)
        el = self.device(className='android.widget.EditText')
        el.set_text('Password003')
        el = self.device(text='Next')
        el.click.wait()
        self.logger.info('add previous account if exists')
        el = self.device(text='ADD PREVIOUS ACCOUNT')
        if el.wait.exists(timeout=20000):
            el.click.wait()
        else:
            self.logger.info('wait I agree')
            el = self.device(text='I agree')
            el.click.wait()
        self.logger.info('wait check')
        time.sleep(20)
        self.logger.info('wait checking info gone')
        el = self.device(textStartsWith='Checking info')
        el.wait.gone(timeout=120000)
        self.logger.info('skip unlock with fingerprint')
        el = self.device(textMatches='skip|SKIP')
        el.click.wait()
        self.logger.info('skip set a screen lock')
        el = self.device(textMatches='skip|SKIP')
        el.click.wait()
        el = self.device(textMatches='skip anyway|SKIP ANYWAY')
        el.click.wait()
        self.logger.info('skip unlock with face')
        el = self.device(text='Skip')
        el.click.wait()
        # google services
        el = self.device(textMatches='more|MORE')
        self.logger.info('click more for 5 times')
        for i in range(5):
            if el.wait.exists(timeout=5000):
                el.click()
        el = self.device(textMatches='accept|ACCEPT')
        el.click.wait()
        self.logger.info('anything else')
        el = self.device(textMatches='no thanks|NO THANKS')
        el.click.wait()
        self.logger.info('finish finally')
        el = self.device(textMatches='finish|FINISH')
        el.click.wait()
        self.logger.info('finish again')
        el = self.device(textMatches='finish|FINISH')
        el.click.wait()
        self.logger.info('got it got it')
        el = self.device(textMatches='got it|GOT IT')
        el.click.wait()
    # perteam003@gmail.com / Password003


if __name__ == '__main__':
    device_id = utils.get_connected_device()
    s = SetupWiz(device_id, 'setup wiz')
    s.setup()

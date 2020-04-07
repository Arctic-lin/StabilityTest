from lib.chrome import Chrome
from lib.cts_device import CTSDevice
from lib.hub import Hub
from lib.settings import Settings
from lib import adbcommon


def main(device_id=''):
    c = Chrome(device_id)
    c.wakeup()
    c.keep_screen_on()
    c.setup()

    cts = CTSDevice(device_id)
    cts.setup()


if __name__ == '__main__':
    device_id = adbcommon.get_connected_device()
    main(device_id)

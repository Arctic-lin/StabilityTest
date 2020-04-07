import os
import sys
import argparse
lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(lib_path)

import tcl_launcher_jankiness
import gmail_jankiness
import chrome_jankiness
import cts_device_jankiness
from heavy import heavy_test

from lib import adbcommon


def main(device_id, is_heavy=False):
    adbcommon.device_wake(device_id)
    tcl_launcher_jankiness.main(device_id, is_heavy)
    gmail_jankiness.main(device_id, is_heavy)
    chrome_jankiness.main(device_id, is_heavy)
    cts_device_jankiness.main(device_id, is_heavy)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='android device serial use first device if not assigned', action='store', default='')
    parser.add_argument('-H', '--heavy', help='heavy mode', action='store_true', default=False)
    parser.add_argument('-m', '--memory', help='oom level in mb in heavy mode default 325', action='store', default=325, type=int)
    args = parser.parse_args()
    device_id = args.device
    if not device_id:
        device_id = adbcommon.get_connected_device()
    if args.heavy:
        heavy_test.heavy_mode(device_id, args.memory, main, device_id, is_heavy=args.heavy)
    else:
        main(device_id)

import os
import re
import subprocess


def run_command(cmd):
    cmds = []
    t = type(cmd)
    if t is str:
        cmds = cmd.split()
    elif t is list:
        cmds = cmd
    else:
        raise Exception('type {} is not supported'.format(t))
    output = subprocess.check_output(cmds)
    return output


def get_connected_devices():
    pattern = '([\w]*)\s+device\s+$'
    output = run_command('adb devices')
    devices = re.findall(pattern, output, re.M)
    devices = [d.strip() for d in devices if d.strip()]
    return devices


def get_connected_device():
    devices = get_connected_devices()
    if len(devices) > 0:
        return devices[0]
    else:
        raise Exception('no devices connected')


def get_m_device():
    mdevice = os.environ.get("MDEVICE")
    mdevice = mdevice if mdevice else get_connected_device()
    # mdevice = mdevice if mdevice else '7e119e2c'
    return mdevice

def get_s_device():
    sdevice = os.environ.get("SDEVICE")
    return sdevice
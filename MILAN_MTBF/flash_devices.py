import math
import os
import re
import subprocess
import tempfile
import threading
import time

import requests
from pyquery import PyQuery as pq
from tqdm import tqdm


class Spider(object):

    def __init__(self, root_url):
        self.root_url = root_url
        self.urls = []

    def visit(self, url):
        resp = requests.get(url, headers={'Authorization': 'Basic bmJyb290U2g6bmI0NTZTaCM='}, verify=False)
        d = pq(resp.content)
        rs = d('td>a')
        for r in rs:
            href = r.attrib['href']
            if href == '/':
                continue
            if href.startswith('/'):
                href = href[1:]
            url1 = url + href
            if 'parent' in r.text.lower():
                continue
            self.urls.append(url1)
            if '.' not in href:
                self.visit(url1)

    def start(self):
        self.visit(self.root_url)


def get_latest_rom():
    root_url = 'https://172.16.11.171/sync_from_hz/Android_SP/'
    s = Spider(root_url)
    s.start()
    urls = [url for url in s.urls if 'YQ' in url and url.endswith('.mbn')]
    urls = sorted(urls, reverse=True)
    return urls[0]


def download_image():
    url = get_latest_rom()
    localfile = url.split('/')[-1]
    print 'latest image name {}'.format(localfile)
    local_path = os.path.join(tempfile.gettempdir(), localfile)
    r = requests.get(url, stream=True, headers={'Authorization': 'Basic bmJyb290U2g6bmI0NTZTaCM='}, verify=False)
    print 'download image {}'.format(localfile)
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024
    wrote = 0
    with open(local_path, 'wb') as f:
        for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size // block_size), unit='KB',
                         unit_scale=True):
            wrote = wrote + len(data)
            f.write(data)
    if total_size != 0 and wrote != total_size:
        print("ERROR, something went wrong")
    return local_path


def flash_device(device_id, image_path):
    print 'flash device {}'.format(device_id)
    os.system('adb -s {} reboot bootloader'.format(device_id))
    time.sleep(10)
    os.system('fastboot -s {} flash system {}'.format(device_id, image_path))
    time.sleep(10)
    os.system('fastboot -s {} reboot'.format(device_id))


def list_devices():
    output = subprocess.check_output(['adb', 'devices'])
    rs = re.findall('^(.*)\s+device$', output, re.M)
    return rs


if __name__ == '__main__':
    # image_path = download_image()
    # devices = list_devices()
    # threads = []
    # for device in devices:
    #     t = threading.Thread(target=flash_device, args=(device, image_path))
    #     threads.append(t)
    # for t in threads:
    #     t.start()
    # for t in threads:
    #     t.join()
    test =get_latest_rom()
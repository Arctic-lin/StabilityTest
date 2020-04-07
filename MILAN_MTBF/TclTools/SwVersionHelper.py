#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: SwVersionHelper.py
@time: 2017/10/20 10:14

this script help you get software version and download software
"""
import os
import ssl
import sys
import time
import urllib

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if LIB_PATH not in sys.path:
    sys.path.append(LIB_PATH)

from XmlHelper import *
from TclTools.MailHelper import MailHelper


def get_last_sw(url, keyword_in_sw):
    """
    在给定的branch url下，获取到所有的软件版本，反向遍历，找到最新的版本
    进入这个版本的连接，获取所有zip包的信息。
    反向遍历，包括给定的关键字但是不包括signed
    如果其中包括lock，软件还没有同步好，等待1个小时，最多等待4个小时
    如果没有lock，返回最终可以用于下载的软件版本
    :param url:
    :param keyword_in_sw:
    :return:
    """
    # get all versions https://172.16.11.174/teleweb/sync_from_bb/bb_master_aospn-msm8953-tcl/
    context = ssl._create_unverified_context()
    content = urllib.urlopen(url, context=context)
    versions_in_current_branch = content.readlines()  # 拿到了当前分支下的所有软件版本.
    final_url_for_downlaod = ""
    time_for_sync = 3600
    time_for_sync_loops = 4

    # 反向遍历拿到的版本信息，
    for line in reversed(versions_in_current_branch):
        if '<a href="A' in line:
            # version = AAO262
            version = get_text(line)
            software_full_path = url + version
            # 自动触发测试任务，一般放在凌晨3-4点，如果版本没有同步不好，就等待1小时，最多等待4个小时，如果还没有同步好，换其他版本
            for i in range(time_for_sync_loops):
                content_zip = urllib.urlopen(software_full_path, context=context)
                zips_in_current_version = content_zip.readlines()
                # 反向遍历拿到的zip包，这里要注意，有的时候会存在版本还在同步，也就是lock状态，如果lock，等待1小时，直到版本同步完成
                for item in reversed(zips_in_current_version):
                    if keyword_in_sw in item and "signed" not in item:  # found expect string
                        if "lock" in item:  # lock found，sleep
                            print "the file is locked, let's wait for %ss" % time_for_sync
                            time.sleep(time_for_sync)
                        else:  # no lock found, set final string
                            ##由于最近同步软件不存在lock 文件,所以需要判断最后一个字符串是否大于等于3GB
                            item_list = item.split()
                            sw_size = item_list[-1]
                            print "the software %s size is %s" % (version, sw_size)
                            if "G" in sw_size:
                                if int(sw_size.replace("G", "")) >= 3:
                                    print "The compression package is 3 GB+ ,it can be downloaded."
                                else:
                                    print "The compression package is less than 3 GB , can not be downloaded,try next one"
                                    continue
                            else:
                                print "The compression package is less than 1 GB and can not be downloaded.try next one"
                                continue
                            final_url_for_downlaod = software_full_path + get_text(item)
                            print "the final download url is ", final_url_for_downlaod
                            return final_url_for_downlaod
                        break
                else:
                    print "can not find keyword %s in %s" % (keyword_in_sw, version)
                    break
                content_zip.close()
            else:
                print "we had wait for %s*%ss, let's try another one" % (time_for_sync_loops, time_for_sync)

    content.close()
    # print final_url_for_downlaod
    # return final_url_for_downlaod


def get_text(context):
    return context[context.find('>') + 1:context.find('</a>')]


def download_sw(final_url_for_download):
    """
    perform wget cmd
    :param final_url_for_download:
    :return:
    """
    wget_command = "wget %s --no-check-certificate -O build.zip" % final_url_for_download
    print "wget_command:" + wget_command
    subprocess.call(wget_command, shell=True)


def download_sw_version(url, keyword_in_sw):
    """
    try to downlaod sw
    a: https://172.16.11.174/teleweb/sync_from_bb/bb_master_aospn-msm8953-tcl/
    b: https://172.16.11.174/teleweb/sync_from_bb/bb_master_aospn-msm8953-tcl/AAH823/bbry_qc8953_sfi-userdebug-AAH823.zip
    if a, get the last version first, then call download
    if b, just call download
    :param keyword_in_sw: the key word help for search last sw
    :param url: a branch or zip file
    :return:
    """
    final_url_for_download = url
    test_mode = "manual"
    if ".zip" not in url:  # a branch's url
        final_url_for_download = get_last_sw(url, keyword_in_sw)
        test_mode = "daily"

    version_txt = "C:\\%s\\sw_version.txt" % project
    sw_version = final_url_for_download[final_url_for_download.rindex("/", 0, final_url_for_download.rindex("/") - 1
                                                                      ) + 1:final_url_for_download.rindex("/")]

    record_url(final_url_for_download)
    if not os.path.exists(version_txt):
        print "the sw_version.txt is not exists,create new one"
        if not os.path.exists("C:\\%s" % project):
            os.makedirs(r"C:\\%s" % project)
        fp = open(version_txt, "w")
        fp.write("0")
        fp.close()

    # region check the sw version whether is higher than last test. If no, stop test.
    if ".zip" not in url:
        print "current version is " + sw_version
        if not os.path.exists(version_txt):
            print "the sw_version.txt is not exists"
            last_sw_version = "0"
        else:
            with open(version_txt, "r", ) as f:
                last_sw_version = f.read().strip()
                print "last sw version is " + last_sw_version
        if not sw_version > last_sw_version:
            print "this version is not higher than last versioin <%s>. Return!!!" % last_sw_version
            if cancel_flag:
                mail = MailHelper()
                # mail.send_cancel_mail(project, last_sw_version,test_plan_type, email_list)
            return False
            # endregion
    with open(version_txt, "w", ) as f:
        f.write(sw_version)

    download_sw(final_url_for_download)

    build_name = final_url_for_download[final_url_for_download.rindex("/") + 1:final_url_for_download.rindex(".zip")]

    branch_list = final_url_for_download.split("/")
    branch = branch_list[-3]
    if branch == "SFI":
        branch = "Master"
    elif "master" in branch:
        branch = "Master"

    xml.set_data(elem_tag="branch_for_smoke", elem_attrib="value", value=branch)
    xml.set_data(elem_tag="test_mode", elem_attrib="value", value=test_mode)
    xml.set_data(elem_tag="build_name", elem_attrib="value", value=build_name)


def record_url(url):
    url_txt = "C:\\%s\\url.txt" % project
    if not os.path.exists(url_txt):
        if not os.path.exists("C:\\%s" % project):
            os.makedirs(r"C:\\%s" % project)
        fp = open(url_txt, "w")
        fp.write("0")
        fp.close()
    with open(url_txt, "w", ) as f:
        f.write(url)


if __name__ == '__main__':

    cancel_flag = False
    url_for_download = sys.argv[1]
    keyword_in_sw = sys.argv[2]
    if len(sys.argv) >= 6:
        project = sys.argv[3]
        test_plan_type = sys.argv[4]
        email_list = sys.argv[5]
        cancel_flag = True
        print "project:", project
    # url_for_download = "https://172.16.11.174/teleweb/sync_from_bb/bb_release_avengers_mercury_mr_aospn-msm8953-tcl/AAQ557/bbry_qc8953_sfi-user-AAQ557.zip"
    # keyword_in_sw = "bbry_qc8953_sfi-user"
    xml = XmlHelper()
    xml.create_file()
    download_sw_version(url_for_download, keyword_in_sw)

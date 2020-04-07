#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
Auto start TeamViewer and take a snapshot, send the snapshot by Email.
"""

import os
import smtplib
import sys
import time
import traceback
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from PIL import ImageGrab

SHOT_PATH = r"C:\smoke"
if not os.path.exists(SHOT_PATH):
    os.mkdir(SHOT_PATH)


def start_team_viewer(file_path):
    os.startfile(file_path)
    time.sleep(60)
    print "start team viewer finish"


def close_popup(script_path):
    try:
        os.startfile(script_path)
    except:
        print traceback.format_exc()


def snapshot():
    im = ImageGrab.grab()
    im.save(SHOT_PATH + "\\team.jpg")
    print "snapshot finish"


def send_mail(subject, to_addrs):
    username = "ta-nb/nb.valreport"
    password = 'NBvalreport'
    mail_sender = 'valreport@tcl.com'

    msg = MIMEMultipart('TeamViewer')
    msg['Subject'] = subject
    msg['to'] = to_addrs
    msg['from'] = mail_sender
    contacts = msg['to'].split(',') if "," in to_addrs else msg['to']

    smtp = smtplib.SMTP()
    smtp.connect('mail.tcl.com:25')
    smtp.login(username, password)

    fp = open(SHOT_PATH + "\\team.jpg", 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)

    smtp.sendmail(msg['from'], contacts, msg.as_string())
    print "send Email to %s successfully!" % msg['to']
    smtp.quit()


if __name__ == '__main__':
    pc_alias = sys.argv[1]
    mail_receiver = sys.argv[2]
    team_viewer_path = sys.argv[3]

    title = "%s's teamviewer infomation" % pc_alias

    start_team_viewer(team_viewer_path)

    close_popup_script = r"C:\smoke\autoit.exe"
    close_popup(close_popup_script)

    snapshot()
    send_mail(title, mail_receiver)

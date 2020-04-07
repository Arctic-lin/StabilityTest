#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: MailHelper.py
@time: 2017/10/24 13:24

information about this file
"""
import os
import smtplib
import traceback
from email.mime.text import MIMEText

import html_report
from TclTools.XmlHelper import XmlHelper


def verify_parameters(func):
    """
    basic check parameters
    :param func:
    :return:
    """
    print "verify parameters"

    def inner(self, to_addrs, project_name, sw_version, test_plan, test_mode, test_status, html_report):
        try:
            assert to_addrs is not None, "to addrs:%s is incorrect" % to_addrs
            assert sw_version is not None, "SW version:%s is incorrect, can't be None" % sw_version
            assert test_plan is not None and (
                        test_plan.lower() == "smoke" or test_plan.lower() == "mpchecklist"), "test plan should be 'smoke' or 'mpchecklist', but %s got" % test_plan
            assert test_mode is not None and (
                        test_mode.lower() == "daily" or test_mode.lower() == "manual"), "test mode should be 'daily' or 'manual', but %s got" % test_mode
            assert test_status is not None and (
                        test_status.lower() == "started" or test_status.lower() == "finished"), "test status should be 'started' or 'finished', but %s got" % test_status
        except:
            print "parameters is incorrect, will not perform %s " % func
            print traceback.format_exc()
        else:
            func(self, to_addrs, project_name, sw_version, test_plan, test_mode, test_status, html_report)

    return inner


class MailHelper():
    """
    this class help you send mails
    """

    def __init__(self):
        self.username = "ta-nb/nb.valreport"
        # self.password = 'NBvalreport'
        self.password = 'nb@1234'
        self.mail_sender = 'valreport@tcl.com'
        self.xml = XmlHelper()

    def mail_test_started(self):
        """
        send mail to notice test has been started
        :return:
        """
        self.mail_outbox(test_status="started", html="")

    def mail_test_finished(self, crashed="", loops_show_properties="", loops_show_results=""):
        """

        :param crashed:
        :param loops_show_properties:
        :param loops_show_results:
        :return:
        """
        crashed_str = self.generate_crashed_string(crashed)
        self.mail_outbox(test_status="finished", html="",
                         loops_show_properties=loops_show_properties, loops_show_results=loops_show_results,
                         crashed_str=crashed_str)

    def mail_test_finished_for_mp(self, html):
        test_status = "finished"
        email_list_for_mp, _, project_name, sw_version, test_plan, test_mode = self.get_data()
        self.send_mail(email_list_for_mp, project_name, sw_version, test_plan, test_mode, test_status, html)

    def mail_outbox(self, test_status, html, loops_show_properties="", loops_show_results="", crashed_str=""):
        """
        perform mail deliver
        :param test_status: should be started or finished, if finished, generate new html report
        :param html_report: html report for mail sending
        :param generate_new: generate new html with next parameters loops_show_properties, loops_show_results
        :param loops_show_properties: this string will be replace to keywords {loops_show_properties} in html template
                                    the string can be a customized table:<tr><td></td><tr>
        :param loops_show_results: this string will be replace to keywords {loops_show_results} in html template
                                    the string can be a customized table:<tr><td></td><tr>
        :return:
        """
        email_list_for_mp, email_list_for_smoke, project_name, sw_version, test_plan, test_mode = self.get_data()
        branch_for_smoke, device_for_smoke, build_name = self.get_data_for_smoke()

        # version check
        # assert sw_version in build_name, "version(%s) got from device should equal version(%s)got from url" % (sw_version, build_name)
        if build_name is None or sw_version not in build_name:
            build_name = " !!!ERROR!!!!, build(%s) not equal to sw version %s" % (build_name, sw_version)

        # Athena fail to get project name from adb shell getprop. Lead to the project_name empty
        # Todo: avoid below code after the getprop command can get project name
        if project_name == "":
            project_name = "Athena"

        # generate keywords dict
        kw_dict = {"{project_name}": project_name,
                   "{test_plan}": test_plan,
                   "{sw_version}": sw_version,
                   "{loops_show_properties}": loops_show_properties,
                   "{loops_show_results}": loops_show_results,
                   "{branch_for_smoke}": branch_for_smoke,
                   "{device_for_smoke}": device_for_smoke,
                   "{build_name}": build_name,
                   "{crashed_str}": crashed_str}

        if test_status == "finished":
            html = html_report.modify_html_report_kwd(smoke=True,
                                                      **kw_dict) if "smoke" in test_plan else html_report.modify_html_report_kwd(
                **kw_dict)

        if "smoke" in test_plan:
            self.send_mail(email_list_for_smoke, project_name, sw_version, test_plan, test_mode, test_status, html)
        else:
            self.send_mail(email_list_for_mp, project_name, sw_version, test_plan, test_mode, test_status, html)

    def get_data(self):
        """
        get all data
        :return:
        """

        # get information from xml
        email_list_for_mp = self.xml.get_property_from_xml("email_list_for_mp", "value")
        email_list_for_smoke = self.xml.get_property_from_xml("email_list_for_smoke", "value")
        project_name = self.xml.get_property_from_xml("project_name", "value").capitalize()
        sw_version = self.xml.get_property_from_xml("software_version", "value")
        test_plan_type = self.xml.get_property_from_xml("test_plan_type", "value")
        test_mode = self.xml.get_property_from_xml("test_mode", "value")

        return email_list_for_mp, email_list_for_smoke, project_name, sw_version, test_plan_type, test_mode

    def get_data_for_smoke(self):
        branch_for_smoke = self.xml.get_property_from_xml("branch_for_smoke", "value")
        device_for_smoke = self.xml.get_property_from_xml("device_for_smoke", "value")
        build_name = self.xml.get_property_from_xml("build_name", "value")

        return branch_for_smoke, device_for_smoke, build_name

    def generate_crashed_string(self, crashed):
        """
        generate crashed string for html report.
        :return:
        """
        # todo: generate detailed crashed information

        crashed_str = "***** found crashed, check logs for details *****" if crashed else ""
        return crashed_str

    @verify_parameters
    def send_mail(self, to_addrs, project_name, sw_version, test_plan, test_mode, test_status="started",
                  html_report=""):
        """
        common method for send mail,
        :param to_addrs: mail list
        :param sw_version: test version
        :param test_plan: smoke or mpChecklist
        :param test_mode: daily or manual, test started automatically or manually
        :param test_status: should be 'started' for noticing test begin,
                            'finished' for noticing test end, and should the report
        :param html_report: html report
        :return:
        """
        if test_status.lower() == "cancel":
            subject = "[%s][%s]%s test task %s,because no updated version has been released so far." % (
            project_name, test_plan, test_mode, test_status)
        else:
            subject = "[%s][%s]%s %s test task %s" % (project_name, test_plan, sw_version, test_mode, test_status)

        try:
            # init msg msg['to'] MUST be a string
            msg = MIMEText(html_report, 'html', 'utf-8')
            msg['Subject'] = subject
            msg['to'] = to_addrs
            msg['from'] = self.mail_sender

            contacts = msg['to'].split(',') if "," in to_addrs else msg['to']

            # connect smtp
            smtp = smtplib.SMTP()
            smtp.connect('mail.tcl.com:25')
            smtp.login(self.username, self.password)

            # send mail, if have multi contacts, should be list here,
            smtp.sendmail(msg['from'], contacts, msg.as_string())
            print "send %s daily report to %s successfully!" % (test_plan, msg['to'])

            # quit smtp
            smtp.quit()

        except:
            print "found exception, mail send failed"
            print traceback.format_exc()

    def send_cancel_mail(self, project_name, last_sw_version, test_plan, to_addrs):
        """
        common method for send mail,
        :param to_addrs: mail list
        :param sw_version: test version
        :param test_plan: smoke or mpChecklist
        :param test_mode: daily or manual, test started automatically or manually
        :param test_status: should be 'started' for noticing test begin,
                            'finished' for noticing test end, and should the report
        :param html_report: html report
        :return:
        """

        try:
            # init msg msg['to'] MUST be a string
            subject = "[%s][%s]Daily test task cancel" % (project_name, test_plan)
            html_report = "The latest software is %s,no updated version has been released so far." % last_sw_version
            msg = MIMEText(html_report, 'html', 'utf-8')
            msg['Subject'] = subject
            msg['to'] = to_addrs
            msg['from'] = self.mail_sender

            contacts = msg['to'].split(',') if "," in to_addrs else msg['to']

            # connect smtp
            smtp = smtplib.SMTP()
            smtp.connect('mail.tcl.com:25')
            smtp.login(self.username, self.password)

            # send mail, if have multi contacts, should be list here,
            smtp.sendmail(msg['from'], contacts, msg.as_string())
            print "send %s daily report to %s successfully!" % (test_plan, msg['to'])

            # quit smtp
            smtp.quit()

        except:
            print "found exception, mail send failed"
            print traceback.format_exc()

    def send_customized_mail(self, subject, html_report, to_addrs):
        try:
            # init msg msg['to'] MUST be a string
            msg = MIMEText(html_report, 'html', 'utf-8')
            msg['Subject'] = subject
            msg['to'] = to_addrs
            msg['from'] = self.mail_sender

            contacts = msg['to'].split(',') if "," in to_addrs else msg['to']

            # connect smtp
            smtp = smtplib.SMTP()
            smtp.connect('mail.tcl.com:25')
            smtp.login(self.username, self.password)

            # send mail, if have multi contacts, should be list here,
            smtp.sendmail(msg['from'], contacts, msg.as_string())
            print "send daily report to successfully!"

            # quit smtp
            smtp.quit()

        except:
            print "found exception, mail send failed"
            print traceback.format_exc()

    def generate_html_report2(self, smoke=False, **kwargs):
        """
        load template, replace keywords
        :param project_name:
        :param test_plan:
        :param sw_version:
        :param **kwargs: a dict include all keyword for replace
        :return:
        """
        # load html
        html_list = []

        result_path = os.environ.get("LOG_PATH")
        if result_path is None:
            result_path = os.path.dirname(os.path.dirname(__file__)) + "\\results"

        current = result_path + "\\smoke_result.html" if smoke else result_path + "\\mpchecklist.html"

        with open(current) as template:
            while True:
                line = template.readline()
                print line
                if not line:
                    break
                for key in kwargs.keys():
                    if key in line:
                        line = line.replace(str(key), str(kwargs.get(key)))
                html_list.append(line)

        return "".join(html_list)


if __name__ == '__main__':
    mail = MailHelper()
    mail.send_mail("24388044@qq.com,di.wu@tcl.com", "abc", "AAP303", "", "", test_status="started", html_report="")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2019/8/5 18:59

information about this file
"""


import requests

token = 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJtdGJmLWJvdEB0Y2wuY29tIiwiaWF0IjoxNTY1MDc3MzQ4LCJleHAiOjQ2ODcxNDEzNDh9.mhHK1cuPemYNa9n_GZd5ae3yJ_UbOnlSHhUJql274rZtZUkn9bT4Vlwk5h-_8GPtgpL7lslH5qVyVeBYyZbXLQ'
# tat_host = 'http://172.16.11.190:8801'
tat_host = 'http://172.16.11.195:9901'

def send_mail(content, serial, subject):
    segment = '/api/mtbf/notify'
    body = {
      "content": content,
      "html": True,
      "serial": serial,
      "subject": subject}
    return _do_request('post', segment, body)


def _do_request(method, segment, data):
    headers = {
        'token': token,
        'Content-Type': 'application/json'
    }
    url = '{}{}'.format(tat_host, segment)
    # content = None
    try:
        resp = requests.request(method, url, headers=headers, json=data)
        # print resp.content
        if resp.status_code != 200:
            print("response code is not 200 ok")
            return resp.content
        else:
            content = resp.json()
            if not content['success']:
                print ("request failed")
                return resp.content
            return True
    except Exception as e:
        print(e)
    return False


if __name__ == '__main__':
    print send_mail('test', '10b4f8d8', 'test mail')
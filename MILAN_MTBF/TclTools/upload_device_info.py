#!coding=utf-8
import json
import os
import traceback

import requests

import hw_id_utils
# import path_utils

token = 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJtdGJmLWJvdEB0Y2wuY29tIiwiaWF0IjoxNTU1OTEyNDIzLCJleHAiOjE1NzE0NjQ0MjN9.xMjQQRioKyd9OiJBWvdhOgyg4V-F72jN0HFvRch8LoUvqpfR_1eCjaAtAmx-a-ibS8xbOfBQ4hwIyHNoxnM3og'
tat_host = 'http://172.16.11.195:9900'
influxdb_host = 'http://172.16.11.190:8086'
influxdb_db_name = 'device_stat'

url_device_info = '{}/api/device-info/add'.format(tat_host)
url_agent = '{}/api/agent/status'.format(tat_host)
influxdb_end_point = '{}/write?db={}'.format(influxdb_host, influxdb_db_name)

headers = {
    'Accept': '*/*',
    'Token': token,
    'Content-Type': 'application/json',
}


# token = open('local_token.txt').read()
# tat_host = 'http://127.0.0.1:9900'


def send_device_info(device_dict, logger):
    send_info(device_dict, logger, url_device_info)


def send_agent_info(agent_dict, logger):
    send_info(agent_dict, logger, url_agent)


def send_info(info, logger, url):
    try:
        logger.info('info:%s' % info)
        resp = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(info)
        )
        logger.info('Resp status code: {}, body: {}'.format(resp.status_code, resp.content))
    except requests.exceptions.RequestException:
        logger.warning(traceback.format_exc())


def send_battery_temperature(battery, logger):
    _send_to_influxdb([battery], logger, 'battery_temperature')


def send_battery_level(battery, logger):
    _send_to_influxdb([battery], logger, 'battery_level')


def send_processinfo(process_list, logger):
    _send_to_influxdb(process_list, logger, 'process')


def send_freeram(free_ram, logger):
    _send_to_influxdb([free_ram], logger, 'free_ram')


def send_lostram(lost_ram, logger):
    _send_to_influxdb([lost_ram], logger, 'lost_ram')


def send_cpuinfo(cpu_list, logger):
    _send_to_influxdb(cpu_list, logger, 'cpu')


def send_cpuload(cpuload_dict, logger):
    _send_to_influxdb([cpuload_dict], logger, 'cpu_load')


def send_jank(jank_dict, logger):
    _send_to_influxdb([jank_dict], logger, 'jank_total_count')


def _send_to_influxdb(data_list, logger, measurement):
    lines = []
    for d in data_list:
        meta = ['agent_hw_id={}'.format(hw_id_utils.get_hw_id())]
        for k, v in d.items():
            # skip value in data for meta conjunction
            if k == 'value' or k == 'timestamp':
                continue
            # skip empty value
            if not v:
                continue
            meta.append('{}={}'.format(k, v))
        lines.append('{},{} value={} {:.0f}'.format(measurement, ','.join(meta), d['value'], d['timestamp']))
    content = '\n'.join(lines)
    try:
        resp = requests.post(influxdb_end_point, data=content)
        logger.info('Resp status code: {}, body: {}'.format(resp.status_code, resp.content))
    except requests.exceptions.RequestException:
        logger.warning(traceback.format_exc())

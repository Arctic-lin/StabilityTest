#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
import subprocess


def get_pid():
    print "Start get TAT's pid"
    cmd = "tasklist | findstr TAT"
    pids = []
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines, stderr = proc.communicate()
    proc.wait()
    lines = lines.splitlines()

    for line in lines:
        pid = line.split()[1]
        # print pid
        pids.append(pid)

    print pids
    return pids


def kill_pid(pids):
    for pid in pids:
        cmd = "taskkill /f /pid " + pid
        subprocess.call(cmd)


if __name__ == '__main__':
    pid_list = get_pid()
    kill_pid(pid_list)

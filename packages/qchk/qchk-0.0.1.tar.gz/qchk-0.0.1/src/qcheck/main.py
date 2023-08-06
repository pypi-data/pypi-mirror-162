#!/usr/bin/env python3

# Modified version of https://github.com/redbrick/rbquota/blob/071c16f2e3e3b618d4e5b36f9c67c3f3de99e838/rbquota
# Desc: Pretty display of quota usage
# Auth: Charlie Von Metzradt <phaxx@redbrick.dcu.ie>
# Maintainer: Tom Doyle <gruunday@gmail.com>
# Date: Sat Oct  8 16:11:42 IST 2005
# Last Update: Mon May 11 12:45:21 IST 2020

import datetime
import os
import signal
import sys
import subprocess
import time

def get_quota(command, timeout):
    """
    call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None
    """
    start = time.time()
    process = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        time.sleep(0.1)
        now = time.time()
        if (now - start) > timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            #sys.exit(0)
            return "error this string will never be seen"
    return process.stdout.read()

def colour(percent):
    if percent > 80:
        return 31 # red
    elif percent > 60:
        return 33 # yellow
    else:
        return 32 # green


def run():
    if len(sys.argv) == 2:
        username = sys.argv[1]
    else:
        username = ""
    
    # run quota, read in the output.
    cmd = f"/usr/bin/quota -p -w -Q {username}" 
    quota = get_quota(cmd, 5)
    quota = quota.decode("utf-8")
    
    # split the output into a list.
    quota = quota.split("\n")
    
    labels = quota[1].split()
    values = quota[2].split()
    blocks = [ int(''.join(i for i in values[x] if i.isdigit())) for x in range(1,4)]
    files = [ int(''.join(i for i in values[x] if i.isdigit())) for x in range(5,8)]
    
    # if you change the bar width, you'll also need to change the value in the
    # format string below.
    bar_width = 35.0
    
    # print the header
    if username == "":
        account_owner = "your"
    else:
        account_owner = "%s's" % username
    
    sys.stdout.write("\nStorage space report for %s \033[1;34mSoC\033[0m account:\n" % account_owner)
    
    
    if blocks:
        blocks_percent = (blocks[0] * 1.0 / blocks[1] * 1.0) * 100
        blocks_bar_width = blocks_percent * (bar_width / 100)
    
        if blocks_bar_width > bar_width:
            blocks_bar_width = bar_width
    
        # print the blocks quota
        format = "%8s: |\033[1;%dm%-35s\033[0m|\033[0;33m%3d\033[0m%%, \033[0;33m%4d\033[0mMB used, \033[0;33m%4d\033[0mMB free\n"
        sys.stdout.write(format % ("     storage", colour(blocks_percent), "=" * int(blocks_bar_width), blocks_percent, blocks[0] / 1024, (blocks[1] - blocks[0]) / 1024))
    
    if files:
        if files[1] == 0:
           files_percent = 0
        else:
          files_percent = (files[0] * 1.0 / files[1] * 1.0) * 100
        files_bar_width = files_percent * (bar_width / 100)
    
        if files_bar_width > bar_width:
            files_bar_width = bar_width
    
        # print the files quota
        format = "%8s: |\033[1;%dm%-35s\033[0m|\033[0;33m%3d\033[0m%%, \033[0;33m%4d\033[0mUsed,    \033[0;33m%4d\033[0mFree\n"
        sys.stdout.write(format % ("  file count", colour(files_percent), "=" * int(files_bar_width), files_percent, files[0], (files[1] - files[0])))
    
    sys.stdout.write("\n")

if __name__ == '__main__':
  run()

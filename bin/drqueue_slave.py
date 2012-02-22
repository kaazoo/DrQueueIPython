# -*- coding: utf-8 -*-

"""
DrQueue slave startup script
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""


import os, signal, subprocess, sys, platform, time, socket
from collections import deque
from DrQueue import Client as DrQueueClient


if "DRQUEUE_ROOT" not in os.environ:
    sys.stderr.write("DRQUEUE_ROOT environment variable is not set!\n")
    sys.exit(-1)

if "IPYTHON_DIR" not in os.environ:
    sys.stderr.write("IPYTHON_DIR environment variable is not set!\n")
    sys.exit(-1)

if "DRQUEUE_MASTER" not in os.environ:
    sys.stderr.write("DRQUEUE_MASTER environment variable is not set!\n")
    sys.exit(-1)
else:
    MASTER_IP = os.environ["DRQUEUE_MASTER"]

if "DRQUEUE_SLAVE" in os.environ:
    SLAVE_IP = os.environ["DRQUEUE_SLAVE"]
else:
    SLAVE_IP = socket.gethostbyname(socket.getfqdn())

SIGTERM_SENT = False
SIGINT_SENT = False
IPENGINE_PID = None
IPENGINE_LOGPATH = os.path.join(os.environ["DRQUEUE_ROOT"], "logs", "ipengine_" + SLAVE_IP + ".log")
IPENGINE_LOGFILE = open(IPENGINE_LOGPATH, "ab")
IPENGINE_ID = None
CACHE_TIME = 60

# initialize DrQueue client
CLIENT = DrQueueClient()


def sig_handler(signum, frame):
    global IPENGINE_PID
    global SIGINT_SENT
    global SIGTERM_SENT
    global IPENGINE_ID
    global CACHE_TIME
    global CLIENT

    # query information about computer
    comp = CLIENT.identify_computer(IPENGINE_ID, CACHE_TIME)

    # remove computer information and its pool membership if any
    if CLIENT.computer_get_pools(comp) != []:
        CLIENT.computer_delete(comp)

    # handle SIGINT
    if signum == signal.SIGINT:
        sys.stderr.write("Received SIGINT. Shutting Down.\n")
        if not SIGINT_SENT:
            SIGINT_SENT = True
            if IPENGINE_PID > 0:
                sys.stderr.write("Sending INT to IPython engine.\n")
                os.kill(IPENGINE_PID, signal.SIGINT)
                os.waitpid(IPENGINE_PID, 0)

    # handle SIGTERM
    if signum == signal.SIGTERM:
        sys.stderr.write("Received SIGTERM. Shutting Down.\n")
        if not SIGTERM_SENT:
            SIGTERM_SENT = True
            if IPENGINE_PID > 0:
                sys.stderr.write("Sending TERM to IPython engine.\n")
                os.kill(IPENGINE_PID, signal.SIGTERM)
                os.waitpid(IPENGINE_PID, 0)

    sys.exit()


def run_command(command):
    global IPENGINE_LOGFILE

    # execute process and write output to logfile
    try:
        p = subprocess.Popen(command, shell=True, stdout=IPENGINE_LOGFILE, stderr=subprocess.STDOUT)
    except OSError as e:
        errno, strerror = e.args
        message = "OSError({0}) while executing command: {1}\n".format(errno, strerror)
        IPENGINE_LOGFILE.write(message)
        raise OSError(message)
        return False
    return p


def extract_engine_id():
    global IPENGINE_LOGFILE
    global IPENGINE_LOGPATH

    # flush buffers
    IPENGINE_LOGFILE.flush()
    os.fsync(IPENGINE_LOGFILE.fileno())
    time.sleep(1)
    # get last line of logfile
    line = deque(open(IPENGINE_LOGPATH), 1)
    # extract id
    slave_id = int(str(line[0]).split(" ")[-1])
    return slave_id


def main():
    global MASTER_IP
    global SLAVE_IP
    global IPENGINE_LOGPATH
    global IPENGINE_PID
    global IPENGINE_ID
    global CACHE_TIME
    global CLIENT

    # register signal handler for SIGINT & SIGTERM
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    pid = os.getpid()
    print("Running DrQueue slave on " + SLAVE_IP + " with PID " + str(pid) + ".")
    print("Connecting to DrQueue master at " + MASTER_IP + ".")

    # start IPython engine
    command = "ipengine --url tcp://" + MASTER_IP + ":10101"
    ipengine_daemon = run_command(command)
    IPENGINE_PID = ipengine_daemon.pid
    print("IPython engine started with PID " + str(IPENGINE_PID) + ". Logging to " + IPENGINE_LOGPATH + ".")

    # get engine id
    IPENGINE_ID = extract_engine_id()
    print("Registered with id " + str(IPENGINE_ID) + ".")
    time.sleep(6)

    # query information about computer
    comp = CLIENT.identify_computer(IPENGINE_ID, CACHE_TIME)

    # remove computer information and its pool membership if any
    if CLIENT.computer_get_pools(comp) != []:
        CLIENT.computer_delete(comp)

    # set pool directly after startup
    if "DRQUEUE_POOL" in os.environ:
        CLIENT.computer_set_pools(comp, os.environ["DRQUEUE_POOL"].split(","))

    # wait for process to exit
    os.waitpid(ipengine_daemon.pid, 0)


if __name__== "__main__":
    main()


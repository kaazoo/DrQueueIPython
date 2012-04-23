# -*- coding: utf-8 -*-

"""
DrQueue slave startup script
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""


import os, signal, subprocess, sys, platform, time, socket, datetime
from collections import deque
import pkg_resources


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
dist_egg = pkg_resources.get_distribution("DrQueueIPython")
STARTUP_SCRIPT = dist_egg.get_resource_filename(__name__, "EGG-INFO/scripts/get_slave_information.py")


def sig_handler(signum, frame):
    global IPENGINE_PID
    global SIGINT_SENT
    global SIGTERM_SENT

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


def main():
    global MASTER_IP
    global SLAVE_IP
    global IPENGINE_LOGPATH
    global IPENGINE_PID
    global STARTUP_SCRIPT
    global CACHE_TIME

    # register signal handler for SIGINT & SIGTERM
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    pid = os.getpid()
    print("Running DrQueue slave on " + SLAVE_IP + " with PID " + str(pid) + ".")
    print("Connecting to DrQueue master at " + MASTER_IP + ".")

    # restart ipengine if it was shut down by IPython
    while True:
        # start IPython engine along with startup script
        command = "ipengine --url tcp://" + MASTER_IP + ":10101 -s " + STARTUP_SCRIPT
        ipengine_daemon = run_command(command)
        IPENGINE_PID = ipengine_daemon.pid
        print("IPython engine started with PID " + str(IPENGINE_PID) + ". Logging to " + IPENGINE_LOGPATH + ".")

        # wait for process to exit
        os.waitpid(IPENGINE_PID, 0)

        print("IPython was shut down. Restarting ...")
        time.sleep(5)


if __name__== "__main__":
    main()


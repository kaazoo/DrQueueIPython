# -*- coding: utf-8 -*-

"""
DrQueue slave startup script
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""


import os, signal, subprocess, sys, platform, time, socket

if "DRQUEUE_SLAVE" in os.environ:
    SLAVE_IP = os.environ["DRQUEUE_SLAVE"]
else:
    SLAVE_IP = socket.gethostbyname(socket.getfqdn())

SIGTERM_SENT = False
SIGINT_SENT = False
IPENGINE_PID = None


def sig_handler(signum, frame):
    sig_name = tuple((v) for v, k in signal.__dict__.iteritems() if k == signum)[0]
    sys.stderr.write("Received " + sig_name + ". Shutting Down.\n")

    global IPENGINE_PID

    if sig_name == "SIGINT":
        global SIGINT_SENT
        if not SIGINT_SENT:
            SIGINT_SENT = True
            if IPENGINE_PID > 0:
                sys.stderr.write("Sending INT to IPython engine.\n")
                os.kill(IPENGINE_PID, signal.SIGINT)
                os.waitpid(IPENGINE_PID, 0)

    if sig_name == "SIGTERM":
        global SIGTERM_SENT
        if not SIGTERM_SENT:
            SIGTERM_SENT = True
            if IPENGINE_PID > 0:
                sys.stderr.write("Sending TERM to IPython engine.\n")
                os.kill(IPENGINE_PID, signal.SIGTERM)
                os.waitpid(IPENGINE_PID, 0)

    sys.exit()


def run_command(command, logfile):
    try:
        p = subprocess.Popen(command, shell=True, stdout=logfile, stderr=subprocess.STDOUT)
    except OSError as e:
        errno, strerror = e.args
        message = "OSError({0}) while executing renderer: {1}\n".format(errno, strerror)
        logfile.write(message)
        raise OSError(message)
        return False
    return p


def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

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

    global SLAVE_IP
    pid = os.getpid()
    print("Running DrQueue slave on " + SLAVE_IP + " with PID " + str(pid) + ".")

    # start IPython engine
    command = "ipengine --url tcp://" + MASTER_IP + ":10101"
    ipengine_logpath = os.path.join(os.environ["DRQUEUE_ROOT"], "logs", "ipengine.log")
    ipengine_logfile = open(ipengine_logpath, "ab")
    ipengine_daemon = run_command(command, ipengine_logfile)
    global IPENGINE_PID
    IPENGINE_PID = ipengine_daemon.pid
    print("IPython engine started with PID " + str(ipengine_daemon.pid) + ". Logging to " + ipengine_logpath + ".")

    # wait for any child to exit
    os.wait()


if __name__== "__main__":
    main()


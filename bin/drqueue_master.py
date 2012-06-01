# -*- coding: utf-8 -*-

"""
DrQueue master startup script
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""


import os, signal, subprocess, sys, platform, time, socket

if "DRQUEUE_MASTER" in os.environ:
    MASTER_IP = os.environ["DRQUEUE_MASTER"]
else:
    MASTER_IP = socket.gethostbyname(socket.getfqdn())


SIGTERM_SENT = False
SIGINT_SENT = False
MONGODB_PID = None
IPCONTROLLER_PID = None


def isOpen(ip,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


def sig_handler(signum, frame):
    global MONGODB_PID
    global IPCONTROLLER_PID

    if signum == signal.SIGINT:
        sys.stderr.write("Received SIGINT. Shutting Down.\n")
        global SIGINT_SENT
        if not SIGINT_SENT:
            SIGINT_SENT = True
            if IPCONTROLLER_PID > 0:
                sys.stderr.write("Sending INT to IPython controller.\n")
                os.kill(IPCONTROLLER_PID, signal.SIGINT)
                os.waitpid(IPCONTROLLER_PID, 0)
            if MONGODB_PID > 0:
                sys.stderr.write("Sending INT to MongoDB.\n")
                os.kill(MONGODB_PID, signal.SIGINT)
                os.waitpid(MONGODB_PID, 0)

    if signum == signal.SIGTERM:
        sys.stderr.write("Received SIGTERM. Shutting Down.\n")
        global SIGTERM_SENT
        if not SIGTERM_SENT:
            SIGTERM_SENT = True
            if IPCONTROLLER_PID > 0:
                sys.stderr.write("Sending TERM to IPython controller.\n")
                os.kill(IPCONTROLLER_PID, signal.SIGTERM)
                os.waitpid(IPCONTROLLER_PID, 0)
            if MONGODB_PID > 0:
                sys.stderr.write("Sending TERM to MongoDB.\n")
                os.kill(MONGODB_PID, signal.SIGTERM)
                os.waitpid(MONGODB_PID, 0)

    sys.exit()


def run_command(command, logfile):
    try:
        p = subprocess.Popen(command, shell=True, stdout=logfile, stderr=subprocess.STDOUT)
    except OSError as e:
        errno, strerror = e.args
        message = "OSError({0}) while executing command: {1}\n".format(errno, strerror)
        logfile.write(message)
        raise OSError(message)
        return False
    return p


def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    global MASTER_IP
    pid = os.getpid()
    print("Running DrQueue master on " + MASTER_IP + " with PID " + str(pid) + ".")

    if "DRQUEUE_ROOT" not in os.environ:
        sys.stderr.write("DRQUEUE_ROOT environment variable is not set!\n")
        sys.exit(-1)

    if "IPYTHONDIR" not in os.environ:
        sys.stderr.write("IPYTHONDIR environment variable is not set!\n")
        sys.exit(-1)

    # start MongoDB daemon
    command = "mongod --dbpath $IPYTHONDIR/db --rest"
    mongodb_logpath = os.path.join(os.environ["DRQUEUE_ROOT"], "logs", "mongodb.log")
    mongodb_logfile = open(mongodb_logpath, "ab")
    mongodb_daemon = run_command(command, mongodb_logfile)
    global MONGODB_PID
    MONGODB_PID = mongodb_daemon.pid
    print("MongoDB started with PID " + str(mongodb_daemon.pid) + ". Logging to " + mongodb_logpath + ".")

    # wait until port 27017 of MongoDB is available
    mongodb_available = False
    while mongodb_available == False:
        mongodb_available = isOpen("127.0.0.1", 27017)
        time.sleep(2)
        print("Waiting for MongoDB to start up . . . ")

    # start IPython controller
    command = "ipcontroller --url tcp://" + MASTER_IP + ":10101 --mongodb"
    ipcontroller_logpath = os.path.join(os.environ["DRQUEUE_ROOT"], "logs", "ipcontroller.log")
    ipcontroller_logfile = open(ipcontroller_logpath, "ab")
    ipcontroller_daemon = run_command(command, ipcontroller_logfile)
    global IPCONTROLLER_PID
    IPCONTROLLER_PID = ipcontroller_daemon.pid
    print("IPython controller started with PID " + str(ipcontroller_daemon.pid) + ". Logging to " + ipcontroller_logpath + ".")

    # wait for any child to exit
    os.wait()


if __name__== "__main__":
    main()





import os, signal, subprocess, sys, platform, time, socket

MASTER_IP = socket.gethostbyname(socket.getfqdn())
SIGTERM_SENT = False
MONGODB_PID = None
IPCONTROLLER_PID = None


def sigterm_handler(signum, frame):
    sys.stderr.write("SIGTERM handler. Shutting Down.\n")

    global SIGTERM_SENT
    global MONGODB_PID
    global IPCONTROLLER_PID

    if not SIGTERM_SENT:
        SIGTERM_SENT = True
        if MONGODB_PID > 0:
            sys.stderr.write("Sending TERM to MongoDB.\n")
            os.kill(MONGODB_PID, signal.SIGTERM)
        if IPCONTROLLER_PID > 0:
            sys.stderr.write("Sending TERM to IPython controller.\n")
            os.kill(IPCONTROLLER_PID, signal.SIGTERM)

    sys.exit()


def run_command(command, logfile):
    try:
        p = subprocess.Popen(command, shell=True, stdout=logfile, stderr=subprocess.STDOUT)
    except OSError as (errno, strerror):
        message = "OSError({0}) while executing renderer: {1}\n".format(errno, strerror)
        logfile.write(message)
        raise OSError(message)
        return False
    return p


def main():
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)

    global MASTER_IP
    print("Running DrQueue master on " + MASTER_IP)

    if os.environ["DRQUEUE_ROOT"] == None:
        sys.stderr.write("DRQUEUE_ROOT environment variable is not set!\n")
        sys.exit(-1)

    if os.environ["IPYTHON_DIR"] == None:
        sys.stderr.write("IPYTHON_DIR environment variable is not set!\n")
        sys.exit(-1)

    # start MongoDB daemon
    command = "mongod --dbpath $IPYTHON_DIR/db"
    mongodb_logfile = open("mongodb.log", "ab")
    mongodb_daemon = run_command(command, mongodb_logfile)
    global MONGODB_PID
    MONGODB_PID = mongodb_daemon.pid
    print("MongoDB started with PID " + str(mongodb_daemon.pid) + ".")

    # wait a short while
    time.sleep(5)

    # start IPython controller
    command = "ipcontroller --url tcp://" + MASTER_IP + ":10101 --mongodb"
    ipcontroller_logfile = open("ipcontroller.log", "ab")
    ipcontroller_daemon = run_command(command, ipcontroller_logfile)
    global IPCONTROLLER_PID
    IPCONTROLLER_PID = ipcontroller_daemon.pid
    print("IPython controller started with PID " + str(ipcontroller_daemon.pid) + ".")

    # wait for any child to exit
    os.wait()


if __name__== "__main__":
    main()


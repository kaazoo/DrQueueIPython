import time
import os
import socket
import DrQueue
from DrQueue import Computer as DrQueueComputer


if "DRQUEUE_SLAVE" in os.environ:
    SLAVE_IP = os.environ["DRQUEUE_SLAVE"]
else:
    SLAVE_IP = socket.gethostbyname(socket.getfqdn())

IPENGINE_LOGPATH = os.path.join(os.environ["DRQUEUE_ROOT"], "logs", "ipengine_startup_" + SLAVE_IP + ".log")
IPENGINE_LOGFILE = open(IPENGINE_LOGPATH, "ab")

# get computer information
engine = DrQueueComputer()
# set creation time
engine['created_at'] = int(time.time())
# store entry in database
DrQueueComputer.store_db(engine)

IPENGINE_LOGFILE.write("Computer info: \n")
IPENGINE_LOGFILE.write(str(engine) + "\n")

IPENGINE_LOGFILE.close
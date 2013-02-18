import time
import os
import socket
import DrQueue
from DrQueue import Computer as DrQueueComputer
from IPython.config.application import Application


if "DRQUEUE_SLAVE" in os.environ:
    SLAVE_IP = os.environ["DRQUEUE_SLAVE"]
else:
    SLAVE_IP = socket.gethostbyname(socket.getfqdn())

IPENGINE_STARTUP_LOGPATH = os.path.join(os.environ["DRQUEUE_ROOT"], "logs", "ipengine_" + SLAVE_IP + ".log")
IPENGINE_STARTUP_LOGFILE = open(IPENGINE_STARTUP_LOGPATH, "ab")

# connect to current IPython engine instance
app = Application.instance()
# get engine_id
engine_id = app.engine.id

# get computer information
engine = DrQueueComputer()
# set creation time
engine['created_at'] = int(time.time())
# set engine_id
engine['engine_id'] = engine_id
# store entry in database
DrQueueComputer.store_db(engine)

IPENGINE_STARTUP_LOGFILE.write("\nComputer info: \n")
IPENGINE_STARTUP_LOGFILE.write(str(engine) + "\n\n")

# flush buffers
IPENGINE_STARTUP_LOGFILE.flush()
os.fsync(IPENGINE_STARTUP_LOGFILE.fileno())

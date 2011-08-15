# -*- coding: utf-8 -*-

import os,signal,subprocess,sys
import os.path
from time import strftime,localtime


# external variables in upper case:
# DRQUEUE_OS
# DRQUEUE_ETC
# DRQUEUE_SCENEFILE
# DRQUEUE_FRAME
# DRQUEUE_BLOCKSIZE
# DRQUEUE_ENDFRAME
# DRQUEUE_RENDERTYPE
# DRQUEUE_LOGFILE
# DRQUEUE_PROJECTDIR
# DRQUEUE_CONFIGDIR
# DRQUEUE_STEPFRAME


# range to render
block = DRQUEUE_FRAME + DRQUEUE_BLOCKSIZE - 1
if block > DRQUEUE_ENDFRAME:
	block = DRQUEUE_ENDFRAME

# renderer path/executable
engine_path="lwsn"

command = engine_path+" -3 -c " + DRQUEUE_CONFIGDIR + " -d " + DRQUEUE_PROJECTDIR + " -q " + DRQUEUE_SCENEFILE + " " + str(DRQUEUE_FRAME) + " " + str(block) + " " + str(DRQUEUE_STEPFRAME)

# write output to logfile
logfile = open(DRQUEUE_LOGFILE, "ab")
logfile.write("Log started at " + strftime("%a, %d %b %Y %H:%M:%S", localtime()) + "\n\n")
logfile.write(command+"\n")
logfile.flush()

# check scenefile
if os.path.isfile(DRQUEUE_SCENEFILE) == False:
    logfile.write("Scenefile was not found. Exiting with status 1.\n\n")
    logfile.close()
    exit(1)

# run renderer and wait for finish
p = subprocess.Popen(command, shell=True, stdout=logfile, stderr=subprocess.STDOUT)
sts = os.waitpid(p.pid, 0)

# return exit status to IPython
logfile.write("Exiting with status " + str(sts[1]) + ".\n\n")
logfile.close()
if sts[1] > 0:
    exit(sts[1])


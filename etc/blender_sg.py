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


# range to render
block = DRQUEUE_FRAME + DRQUEUE_BLOCKSIZE - 1
if block > DRQUEUE_ENDFRAME:
	block = DRQUEUE_ENDFRAME

# renderer path/executable
engine_path="blender"

if DRQUEUE_RENDERTYPE == "animation":
  os.putenv("startframe", str(DRQUEUE_FRAME))
  os.putenv("endframe", str(block))
  command = engine_path+" -b "+DRQUEUE_SCENEFILE+" -P " + os.path.join(DRQUEUE_ETC, "blender_same_directory.py")
else:
  os.putenv("curpart", str(DRQUEUE_FRAME))
  os.outenv("maxparts", str(DRQUEUE_ENDFRAME))
  command = engine_path+" -b "+DRQUEUE_SCENEFILE+" -P " + os.path.join(DRQUEUE_ETC, "blender_region_rendering.py")

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


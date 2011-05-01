# -*- coding: utf-8 -*-

import os,signal,subprocess,sys

os.umask(0)

# external variables in upper case:
# DRQUEUE_OS
# DRQUEUE_ETC
# DRQUEUE_SCENEFILE
# DRQUEUE_FRAME
# DRQUEUE_BLOCKSIZE
# DRQUEUE_ENDFRAME
# DRQUEUE_RENDERTYPE
# DRQUEUE_LOGFILE


if DRQUEUE_OS == "WINDOWS":
	# convert to windows path with drive letter
	DRQUEUE_SCENE = subprocess.Popen(["cygpath.exe", "-w "+DRQUEUE_SCENEFILE], stdout=subprocess.PIPE).communicate()[0]

block = DRQUEUE_FRAME + DRQUEUE_BLOCKSIZE - 1

if block > DRQUEUE_ENDFRAME:
	block = DRQUEUE_ENDFRAME

engine_path="blender"

if DRQUEUE_RENDERTYPE == "animation":
  os.putenv("startframe", str(DRQUEUE_FRAME))
  os.putenv("endframe", str(block))
  command = engine_path+" -b "+DRQUEUE_SCENEFILE+" -P "+DRQUEUE_ETC+"/blender_same_directory.py"
else:
  os.putenv("curpart", str(DRQUEUE_FRAME))
  os.outenv("maxparts", str(DRQUEUE_ENDFRAME))
  command = engine_path+" -b "+DRQUEUE_SCENEFILE+" -P "+DRQUEUE_ETC+"/blender_region_rendering.py"

logfile = open(DRQUEUE_LOGFILE,"wb")
logfile.write(command)
logfile.flush()

p = subprocess.Popen(command, shell=True, stdout=logfile, stderr=subprocess.STDOUT)
sts = os.waitpid(p.pid, 0)


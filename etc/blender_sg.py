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


print(command)
sys.stdout.flush()

p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)

# This should requeue the frame if failed
#if sts[1] != 0:
#	print("Requeueing frame…")
#	os.kill(os.getppid(), signal.SIGINT)
#	exit(1)
#else:
	#if DRQUEUE_OS != "WINDOWS" then:
	# The frame was rendered properly
	# We don't know the output image name. If we knew we could set this correctly
	# chown_block RF_OWNER RD/IMAGE DRQUEUE_FRAME BLOCK 

	# change userid and groupid
	#chown 1002:1004 $SCENE:h/*
#	print("Finished.")
#
# Notice that the exit code of the last command is received by DrQueue
#

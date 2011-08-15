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
# DRQUEUE_RENDERDIR
# DRQUEUE_RENDERTYPE
# DRQUEUE_LOGFILE

if DRQUEUE_OS == "WINDOWS":
  	engine_path = "C:\Program\ Files\MAXON\CINEMA\ 4D\ R12\CINEMA\ 4D.exe"

if DRQUEUE_OS == "OSX":
  	engine_path = "/Applications/MAXON/CINEMA\ 4D\ R12/CINEMA\ 4D.app/Contents/MacOS/CINEMA\ 4D"

if DRQUEUE_OS == "LINUX":
  	# we use wine on linux (this is a hack, but works)
  	# there is a tightvnc server running on display :1
  	# see wine bug #8069
  	# the user running DrQueue slave process needs to have wine and Cinema4D installed

  	# convert to windows path with drive letter
  	DRQUEUE_SCENEFILE = subprocess.Popen(["winepath", "-w "+DRQUEUE_SCENEFILE], stdout=subprocess.PIPE).communicate()[0]
  	DRQUEUE_RENDERDIR = subprocess.Popen(["winepath", "-w "+DRQUEUE_RENDERDIR], stdout=subprocess.PIPE).communicate()[0]

  	workdir = "~/.wine/drive_c/Program\ Files/MAXON/CINEMA\ 4D\ R12"
  	engine_path = "wine CINEMA\ 4D.exe"

  	# change into workdir, better for wine startup
  	os.chdir(workdir)

  	# set env variable, so wine can access the xserver even though we are rendering headless
  	os.environ["DISPLAY"] = ":1"

# range to render
block = DRQUEUE_FRAME + DRQUEUE_BLOCKSIZE - 1
if block > DRQUEUE_ENDFRAME:
	block = DRQUEUE_ENDFRAME

command = engine_path+" -nogui -render "+DRQUEUE_SCENEFILE+" -oimage " + DRQUEUE_RENDERDIR + " -frame " + DRQUEUE_FRAME + " -omultipass " + DRQUEUE_RENDERDIR + " -threads 0"

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


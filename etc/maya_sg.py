# -*- coding: utf-8 -*-

import os,signal,subprocess,sys
import os.path
from time import strftime,localtime


# used external variables in upper case:
# DRQUEUE_OS
# DRQUEUE_ETC
# DRQUEUE_FRAME
# DRQUEUE_BLOCKSIZE
# DRQUEUE_ENDFRAME
# DRQUEUE_SCENEFILE
# DRQUEUE_LOGFILE
# DRQUEUE_IMAGEFILE
# DRQUEUE_CAMERA
# DRQUEUE_RESX
# DRQUEUE_RESY
# DRQUEUE_FILEFORMAT
# DRQUEUE_RENDERER
# DRQUEUE_PRECOMMAND
# DRQUEUE_POSTCOMMAND
# DRQUEUE_RENDERDIR
# DRQUEUE_PROJECTDIR


# range to render
block = DRQUEUE_FRAME + DRQUEUE_BLOCKSIZE - 1
if block > DRQUEUE_ENDFRAME:
	block = DRQUEUE_ENDFRAME

if ("DRQUEUE_IMAGEFILE" in locals()) and (DRQUEUE_IMAGEFILE != ""):
  image_args="-im "+DRQUEUE_IMAGEFILE
else:
  image_args=""

if ("DRQUEUE_CAMERA" in locals()) and (DRQUEUE_CAMERA != ""):
  camera_args="-cam "+DRQUEUE_CAMERA
else:
  camera_args=""

if ("DRQUEUE_RESX" in locals()) and ("DRQUEUE_RESX" in locals()) and (int(DRQUEUE_RESX) > 0) and (int(DRQUEUE_RESY) > 0):
  res_args="-x "+DRQUEUE_RESX+" -y "+DRQUEUE_RESY
else:
  res_args=""

if ("DRQUEUE_FILEFORMAT" in locals()) and (DRQUEUE_FILEFORMAT != ""):
  format_args="-of "+DRQUEUE_FILEFORMAT
else:
  format_args=""

if ("DRQUEUE_RENDERER" in locals()) and (DRQUEUE_RENDERER == "mr"):
  ## number of processors/cores to use
  #proc_args="-rt 2"

  ## use Maya's automatic detection
  proc_args="-art"
elif ("DRQUEUE_RENDERER" in locals()) and (DRQUEUE_RENDERER == "sw"):
  ## number of processors/cores to use
  #proc_args="-n 2"

  ## use Maya's automatic detection
  proc_args="-n 0"
else:
  ## don't add something
  proc_args=""

if ("DRQUEUE_PRECOMMAND" in locals()) and (DRQUEUE_PRECOMMAND != ""):
  pre_args="-preRender \""+DRQUEUE_PRECOMMAND+"\""
else:
  pre_args=""
	
if ("DRQUEUE_POSTCOMMAND" in locals()) and (DRQUEUE_POSTCOMMAND != ""):
  post_args="-postRender \""+DRQUEUE_POSTCOMMAND+"\""
else:
  post_args=""

# renderer path/executable
engine_path="Render"

command = engine_path+" "+pre_args+" "+post_args+" "+proc_args+" -s "+str(DRQUEUE_FRAME)+" -e "+str(block)+" "+res_args+" "+format_args+" -rd "+DRQUEUE_RENDERDIR+" -proj "+DRQUEUE_PROJECTDIR+" -r "+DRQUEUE_RENDERER+" "+image_args+" "+camera_args+" "+DRQUEUE_SCENEFILE

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


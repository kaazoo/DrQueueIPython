# -*- coding: utf-8 -*-

"""
DrQueue render template for Cinema4D
Copyright (C) 2011-2014 Andreas Schröder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os
import DrQueue
from DrQueue import engine_helpers


def run_renderer(env_dict):

    # define external variables as global
    globals().update(env_dict)
    global DRQUEUE_OS
    global DRQUEUE_ETC
    global DRQUEUE_SCENEFILE
    global DRQUEUE_FRAME
    global DRQUEUE_BLOCKSIZE
    global DRQUEUE_ENDFRAME
    global DRQUEUE_RENDERDIR
    global DRQUEUE_LOGFILE

    # initialize helper object
    helper = engine_helpers.Helper(env_dict['DRQUEUE_LOGFILE'])

    # range to render
    block = helper.calc_block(DRQUEUE_FRAME, DRQUEUE_ENDFRAME, DRQUEUE_BLOCKSIZE)

    if DRQUEUE_OS in ["Windows", "Win32"]:
        DRQUEUE_SCENEFILE = helper.replace_stdpath_with_driveletter(DRQUEUE_SCENEFILE, 'n:')
        # renderer path/executable
      	engine_path = "C:\Program\ Files\MAXON\CINEMA\ 4D\ R12\CINEMA\ 4D.exe"

    elif DRQUEUE_OS in ["Mac OSX", "Darwin"]:
        # renderer path/executable
      	engine_path = "/Applications/MAXON/CINEMA\ 4D\ R12/CINEMA\ 4D.app/Contents/MacOS/CINEMA\ 4D"

    elif DRQUEUE_OS == "Linux":
      	# we use wine on linux (this is a hack, but works)
      	# there is a tightvnc server running on display :1
      	# see wine bug #8069
      	# the user running DrQueue slave process needs to have wine and Cinema4D installed

      	# convert to windows path with drive letter
      	DRQUEUE_SCENEFILE = subprocess.Popen(["winepath", "-w "+DRQUEUE_SCENEFILE], stdout=subprocess.PIPE).communicate()[0]
      	DRQUEUE_RENDERDIR = subprocess.Popen(["winepath", "-w "+DRQUEUE_RENDERDIR], stdout=subprocess.PIPE).communicate()[0]

      	workdir = "~/.wine/drive_c/Program\ Files/MAXON/CINEMA\ 4D\ R12"
      	# renderer path/executable
      	engine_path = "wine CINEMA\ 4D.exe"

      	# change into workdir, better for wine startup
      	os.chdir(workdir)

      	# set env variable, so wine can access the xserver even though we are rendering headless
      	os.environ["DISPLAY"] = ":1"

    else:
        helper.log_write('ERROR: Unsupported operating system ' + str(DRQUEUE_OS))
        return helper.return_to_ipython(1)

    command = engine_path + " -nogui -render " + DRQUEUE_SCENEFILE + " -oimage " + DRQUEUE_RENDERDIR + " -frame " + str(DRQUEUE_FRAME) + " -omultipass " + DRQUEUE_RENDERDIR + " -threads 0"

    # log command line
    helper.log_write(command + "\n")

    # check scenefile
    helper.check_scenefile(DRQUEUE_SCENEFILE)

    # run renderer and wait for finish
    ret = helper.run_command(command)

    # return exit status to IPython
    return helper.return_to_ipython(ret)


# -*- coding: utf-8 -*-

import os, signal, subprocess, sys, platform
from time import strftime,localtime


def run_renderer(env_dict):

    # define external variables as global
    globals().update(env_dict)
    global DRQUEUE_OS
    global DRQUEUE_ETC
    global DRQUEUE_SCENEFILE
    global DRQUEUE_FRAME
    global DRQUEUE_BLOCKSIZE
    global DRQUEUE_ENDFRAME
    global DRQUEUE_RENDERTYPE
    global DRQUEUE_LOGFILE

    # range to render
    block = DRQUEUE_FRAME + DRQUEUE_BLOCKSIZE - 1
    if block > DRQUEUE_ENDFRAME:
    	  block = DRQUEUE_ENDFRAME

    # renderer path/executable
    engine_path="blender"

    # replace paths on Windows
    if DRQUEUE_OS in ["Windows", "Win32"]:
        # replace DrQueue standard Unix path with specific Windows drive letter
        DRQUEUE_SCENEFILE = DRQUEUE_SCENEFILE.replace('/usr/local/drqueue', 'n:')
        DRQUEUE_SCENEFILE = DRQUEUE_SCENEFILE.replace('/', '\\')

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
    logfile.write("Log started at " + strftime("%a, %d %b %Y %H:%M:%S", localtime()) + ".\n")
    logfile.write("Running on " + platform.node() + " under " + DRQUEUE_OS + ".\n\n")
    logfile.write(command + "\n")
    logfile.flush()

    # check scenefile
    if os.path.isfile(DRQUEUE_SCENEFILE) == False:
        message = "Scenefile was not found."
        logfile.write(message)
        logfile.close()
        raise ValueError(message)
        return False

    # run renderer and wait for finish
    try:
        p = subprocess.Popen(command, shell=True, stdout=logfile, stderr=subprocess.STDOUT)
    except OSError as (errno, strerror):
        message = "OSError({0}) while executing renderer: {1}\n".format(errno, strerror)
        logfile.write(message)
        logfile.close()
        raise OSError(message)
        return False
    p.wait()

    # return exit status to IPython
    logfile.write("Exiting with status " + str(p.returncode) + ".\n\n")
    logfile.close()
    if p.returncode > 0:
        return False
    else:
        return True




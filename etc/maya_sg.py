# -*- coding: utf-8 -*-

"""
DrQueue render template for Maya
Copyright (C) 2011 Andreas Schroeder

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
    global DRQUEUE_IMAGEFILE
    global DRQUEUE_CAMERA
    global DRQUEUE_RESX
    global DRQUEUE_RESY
    global DRQUEUE_FILEFORMAT
    global DRQUEUE_RENDERER
    global DRQUEUE_PRECOMMAND
    global DRQUEUE_POSTCOMMAND
    global DRQUEUE_LOGFILE

    # initialize helper object
    helper = engine_helpers.Helper(env_dict['DRQUEUE_LOGFILE'])

    # range to render
    block = helper.calc_block(DRQUEUE_FRAME, DRQUEUE_ENDFRAME, DRQUEUE_BLOCKSIZE)

    # renderer path/executable
    engine_path = "Render"

    # replace paths on Windows
    if DRQUEUE_OS in ["Windows", "Win32"]:
        DRQUEUE_SCENEFILE = helper.replace_stdpath_with_driveletter(DRQUEUE_SCENEFILE, 'n:')
        DRQUEUE_RENDERDIR = helper.replace_stdpath_with_driveletter(DRQUEUE_RENDERDIR, 'n:')
        DRQUEUE_PROJECTDIR = helper.replace_stdpath_with_driveletter(DRQUEUE_PROJECTDIR, 'n:')

    if ("DRQUEUE_IMAGEFILE" in globals()) and (DRQUEUE_IMAGEFILE != ""):
        image_args = "-im " + DRQUEUE_IMAGEFILE
    else:
        image_args = ""

    if ("DRQUEUE_CAMERA" in globals()) and (DRQUEUE_CAMERA != ""):
        camera_args = "-cam " + DRQUEUE_CAMERA
    else:
        camera_args = ""

    if ("DRQUEUE_RESX" in globals()) and ("DRQUEUE_RESX" in globals()) and (int(DRQUEUE_RESX) > 0) and (int(DRQUEUE_RESY) > 0):
        res_args = "-x " + DRQUEUE_RESX + " -y " + DRQUEUE_RESY
    else:
        res_args = ""

    if ("DRQUEUE_FILEFORMAT" in globals()) and (DRQUEUE_FILEFORMAT != ""):
        format_args = "-of " + DRQUEUE_FILEFORMAT
    else:
        format_args = ""

    if ("DRQUEUE_RENDERER" in globals()) and (DRQUEUE_RENDERER == "mr"):
        ## number of processors/cores to use
        #proc_args = "-rt 2"

        ## use Maya's automatic detection
        proc_args = "-art"
    elif ("DRQUEUE_RENDERER" in globals()) and (DRQUEUE_RENDERER == "sw"):
        ## number of processors/cores to use
        #proc_args = "-n 2"

        ## use Maya's automatic detection
        proc_args = "-n 0"
    else:
        ## don't add something
        proc_args = ""

    if ("DRQUEUE_PRECOMMAND" in globals()) and (DRQUEUE_PRECOMMAND != ""):
        pre_args = "-preRender \"" + DRQUEUE_PRECOMMAND + "\""
    else:
        pre_args = ""

    if ("DRQUEUE_POSTCOMMAND" in globals()) and (DRQUEUE_POSTCOMMAND != ""):
        post_args = "-postRender \"" + DRQUEUE_POSTCOMMAND + "\""
    else:
        post_args = ""

    command = engine_path + " " + pre_args + " " + post_args + " " + proc_args + " -s " + str(DRQUEUE_FRAME) + " -e " + str(block) + " " + res_args + " " + format_args + " -rd " + DRQUEUE_RENDERDIR + " -proj " + DRQUEUE_PROJECTDIR + " -r " + DRQUEUE_RENDERER + " " + image_args + " " + camera_args + " " + DRQUEUE_SCENEFILE

    # log command line
    helper.log_write(command + "\n")

    # check scenefile
    helper.check_scenefile(DRQUEUE_SCENEFILE)

    # run renderer and wait for finish
    ret = helper.run_command(command)

    # return exit status to IPython
    return helper.return_to_ipython(ret)


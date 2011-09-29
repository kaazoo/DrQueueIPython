# -*- coding: utf-8 -*-

"""
DrQueue render template for XSI
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
    global DRQUEUE_RESX
    global DRQUEUE_RESY
    global DRQUEUE_RENDERDIR
    global DRQUEUE_SKIPFRAMES
    global DRQUEUE_RENDERPASS
    global DRQUEUE_LOGFILE

    # initialize helper object
    helper = engine_helpers.Helper(env_dict['DRQUEUE_LOGFILE'])

    # range to render
    block = helper.calc_block(DRQUEUE_FRAME, DRQUEUE_ENDFRAME, DRQUEUE_BLOCKSIZE)

    # renderer path/executable
    engine_path = "xsibatch"

    # replace paths on Windows
    if DRQUEUE_OS in ["Windows", "Win32"]:
        DRQUEUE_SCENEFILE = helper.replace_stdpath_with_driveletter(DRQUEUE_SCENEFILE, 'n:')
        DRQUEUE_RENDERDIR = helper.replace_stdpath_with_driveletter(DRQUEUE_RENDERDIR, 'n:')

    if ("DRQUEUE_RESX" in globals()) and ("DRQUEUE_RESX" in globals()) and (int(DRQUEUE_RESX) > 0) and (int(DRQUEUE_RESY) > 0):
        res_args = "-resolutionX " + DRQUEUE_RESX + " -resolutionY " + DRQUEUE_RESY
    else:
        res_args = ""

    if ("DRQUEUE_RENDERPASS" in globals()) and (DRQUEUE_RENDERPASS != ""):
        pass_args = "-pass " + DRQUEUE_RENDERPASS
    else:
        pass_args = ""

    os.chdir(DRQUEUE_RENDERDIR)

    command = engine_path + " -r -scene " + DRQUEUE_SCENEFILE + " -verbose prog -startframe " + str(DRQUEUE_FRAME) + " -endframe " + str(block) + " " + pass_args + " " + res_args + " -skip " + str(DRQUEUE_SKIPFRAMES)

    # log command line
    helper.log_write(command + "\n")

    # check scenefile
    helper.check_scenefile(DRQUEUE_SCENEFILE)

    # run renderer and wait for finish
    ret = helper.run_command(command)

    # return exit status to IPython
    return helper.return_to_ipython(ret)


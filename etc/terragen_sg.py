# -*- coding: utf-8 -*-

"""
DrQueue render template for Terragen
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
    global DRQUEUE_STEPFRAME
    global DRQUEUE_WORLDFILE
    global DRQUEUE_TERRAINFILE
    global DRQUEUE_LOGFILE

    # initialize helper object
    helper = engine_helpers.Helper(env_dict['DRQUEUE_LOGFILE'])

    # range to render
    block = helper.calc_block(DRQUEUE_FRAME, DRQUEUE_ENDFRAME, DRQUEUE_BLOCKSIZE)

    # renderer path/executable
    engine_path = "terragenCLI"

    # replace paths on Windows
    if DRQUEUE_OS in ["Windows", "Win32"]:
        DRQUEUE_SCENEFILE = helper.replace_stdpath_with_driveletter(DRQUEUE_SCENEFILE, 'n:')
        DRQUEUE_WORLDFILE = helper.replace_stdpath_with_driveletter(DRQUEUE_WORLDFILE, 'n:')
        DRQUEUE_TERRAINFILE = helper.replace_stdpath_with_driveletter(DRQUEUE_TERRAINFILE, 'n:')

    command = engine_path + " -hide -exit -w\"" + DRQUEUE_WORLDFILE + "\" -t\"" + DRQUEUE_TERRAINFILE + "\" -s\"" + DRQUEUE_SCENEFILE + "\" " + str(DRQUEUE_FRAME) + " " + str(block) + " " + str(DRQUEUE_STEPFRAME)

    # log command line
    helper.log_write(command + "\n")

    # check scenefile
    helper.check_scenefile(DRQUEUE_SCENEFILE)

    # run renderer and wait for finish
    ret = helper.run_command(command)

    # return exit status to IPython
    return helper.return_to_ipython(ret)


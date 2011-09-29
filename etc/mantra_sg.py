# -*- coding: utf-8 -*-

"""
DrQueue render template for Mantra
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
    global DRQUEUE_CUSTOM_BUCKET
    global DRQUEUE_BUCKETSIZE
    global DRQUEUE_CUSTOM_LOD
    global DRQUEUE_LOD
    global DRQUEUE_CUSTOM_VARYAA
    global DRQUEUE_VARYAA
    global DRQUEUE_RAYTRACE
    global DRQUEUE_ANTIALIAS
    global DRQUEUE_CUSTOM_BDEPTH
    global DRQUEUE_BDEPTH
    global DRQUEUE_CUSTOM_ZDEPTH
    global DRQUEUE_ZDEPTH
    global DRQUEUE_CUSTOM_CRACKS
    global DRQUEUE_CRACKS
    global DRQUEUE_CUSTOM_QUALITY
    global DRQUEUE_QUALITY
    global DRQUEUE_CUSTOM_QFINER
    global DRQUEUE_QFINER
    global DRQUEUE_CUSTOM_SMULTIPLIER
    global DRQUEUE_SMULTIPLIER
    global DRQUEUE_CUSTOM_MPCACHE
    global DRQUEUE_MPCACHE
    global DRQUEUE_CUSTOM_SMPOLYGON
    global DRQUEUE_SMPOLYGON
    global DRQUEUE_CUSTOM_WH
    global DRQUEUE_RESX
    global DRQUEUE_RESY
    global DRQUEUE_CUSTOM_TYPE
    global DRQUEUE_CTYPE
    global DRQUEUE_LOGFILE

    # initialize helper object
    helper = engine_helpers.Helper(env_dict['DRQUEUE_LOGFILE'])

    # range to render
    block = helper.calc_block(DRQUEUE_FRAME, DRQUEUE_ENDFRAME, DRQUEUE_BLOCKSIZE)

    # renderer path/executable
    engine_path = "mantra"

    # replace paths on Windows
    if DRQUEUE_OS in ["Windows", "Win32"]:
        DRQUEUE_SCENEFILE = helper.replace_stdpath_with_driveletter(DRQUEUE_SCENEFILE, 'n:')

    if ("DRQUEUE_CUSTOM_BUCKET" in globals()) and (DRQUEUE_CUSTOM_BUCKET == "yes"):
        bucket_args = "-B " + DRQUEUE_BUCKETSIZE
    else:
        bucket_args = ""

    if ("DRQUEUE_CUSTOM_LOD" in globals()) and (DRQUEUE_CUSTOM_LOD == "yes"):
        lod_args = "-L " + DRQUEUE_LOD
    else:
        lod_args = ""

    if ("DRQUEUE_CUSTOM_VARYAA" in globals()) and (DRQUEUE_CUSTOM_VARYAA == "yes"):
        varyaa_args = "-v " + DRQUEUE_VARYAA
    else:
        varyaa_args = ""

    if ("DRQUEUE_RAYTRACE" in globals()) and (DRQUEUE_RAYTRACE == "yes"):
        raytrace_args = "-r"
    else:
        raytrace_args = ""

    if ("DRQUEUE_ANTIALIAS" in globals()) and (DRQUEUE_ANTIALIAS == "yes"):
        antialias_args = "-A"
    else:
        antialias_args = ""

    if ("DRQUEUE_CUSTOM_BDEPTH" in globals()) and (DRQUEUE_CUSTOM_BDEPTH == "yes"):
        bdepth_args = "-b " + DRQUEUE_BDEPTH
    else:
        bdepth_args = ""

    if ("DRQUEUE_CUSTOM_ZDEPTH" in globals()) and (DRQUEUE_CUSTOM_ZDEPTH == "yes"):
        if DRQUEUE_ZDEPTH == "average":
    		    zdepth_args = "-z"
        else:
    		    zdepth_args = "-Z"
    else:
        zdepth_args = ""

    if ("DRQUEUE_CUSTOM_CRACKS" in globals()) and (DRQUEUE_CUSTOM_CRACKS == "yes"):
        cracks_args = "-c " + DRQUEUE_CRACKS
    else:
        cracks_args = ""

    if ("DRQUEUE_CUSTOM_QUALITY" in globals()) and (DRQUEUE_CUSTOM_QUALITY == "yes"):
        quality_args = "-q " + DRQUEUE_QUALITY
    else:
        quality_args = ""

    if ("DRQUEUE_CUSTOM_QFINER" in globals()) and (DRQUEUE_CUSTOM_QFINER == "yes"):
        qfiner_args = "-Q " + DRQUEUE_QFINER
    else:
        qfiner_args = ""

    if ("DRQUEUE_CUSTOM_SMULTIPLIER" in globals()) and (DRQUEUE_CUSTOM_SMULTIPLIER == "yes"):
        smultiplier_args = "-s " + DRQUEUE_SMULTIPLIER
    else:
        smultiplier_args = ""

    if ("DRQUEUE_CUSTOM_MPCACHE" in globals()) and (DRQUEUE_CUSTOM_MPCACHE == "yes"):
        mpcache_args = "-G " + DRQUEUE_MPCACHE
    else:
        mpcache_args = ""

    if ("DRQUEUE_CUSTOM_MCACHE" in globals()) and (DRQUEUE_CUSTOM_MCACHE == "yes"):
        mcache_args = "-G " + DRQUEUE_MCACHE
    else:
        mcache_args = ""

    if ("DRQUEUE_CUSTOM_SMPOLYGON" in globals()) and (DRQUEUE_CUSTOM_SMPOLYGON == "yes"):
        smpolygon_args = "-S " + DRQUEUE_SMPOLYGON
    else:
        smpolygon_args = ""

    if ("DRQUEUE_CUSTOM_WH" in globals()) and (DRQUEUE_CUSTOM_WH == "yes"):
        width_args = "-w " + DRQUEUE_RESX
        height_args = "-w " + DRQUEUE_RESY
    else:
        width_args = ""
        height_args = ""

    if ("DRQUEUE_CUSTOM_TYPE" in globals()) and (DRQUEUE_CUSTOM_TYPE == "yes"):
        type_args = "." + DRQUEUE_CTYPE
    else:
        type_args = ""

    command = engine_path + " -f " + str(DRQUEUE_SCENEFILE + DRQUEUE_PADFRAME) + ".ifd " + antialias_args + " " + raytrace_args + " " + bucket_args + " " + lod_args + "  " + varyaa_args + " " + bdepth_args + " " + zdepth_args + " " + cracks_args + " " + quality_args + " " + qfiner_args + " " + smultiplier_args + " " + mpcache_args + " " + mcache_args + " " + smpolygon_args + " " + width_args + " " + height_args + " " + DRQUEUE_RENDERDIR + str(DRQUEUE_PADFRAME) + type_args

    # log command line
    helper.log_write(command + "\n")

    # check scenefile
    helper.check_scenefile(DRQUEUE_SCENEFILE)

    # run renderer and wait for finish
    ret = helper.run_command(command)

    # return exit status to IPython
    return helper.return_to_ipython(ret)


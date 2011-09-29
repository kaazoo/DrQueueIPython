# -*- coding: utf-8 -*-

"""
DrQueue render template for Mental Ray
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
    global DRQUEUE_RENDERDIR
    global DRQUEUE_IMAGE
    global DRQUEUE_CAMERA
    global DRQUEUE_RESX
    global DRQUEUE_RESY
    global DRQUEUE_FILEFORMAT
    global DRQUEUE_RENDERTYPE
    global DRQUEUE_LOGFILE

    # initialize helper object
    helper = engine_helpers.Helper(env_dict['DRQUEUE_LOGFILE'])

    # range to render
    block = helper.calc_block(DRQUEUE_FRAME, DRQUEUE_ENDFRAME, DRQUEUE_BLOCKSIZE)

    # renderer path/executable
    engine_path = "ray"

    # replace paths on Windows
    if DRQUEUE_OS in ["Windows", "Win32"]:
        DRQUEUE_SCENEFILE = helper.replace_stdpath_with_driveletter(DRQUEUE_SCENEFILE, 'n:')
        DRQUEUE_RENDERDIR = helper.replace_stdpath_with_driveletter(DRQUEUE_RENDERDIR, 'n:')

    if ("DRQUEUE_IMAGEFILE" in globals()) and (DRQUEUE_IMAGEFILE != ""):
        image_args = "-im " + DRQUEUE_IMAGEFILE
    else:
        image_args = ""

    if ("DRQUEUE_CAMERA" in globals()) and (DRQUEUE_CAMERA != ""):
        camera_args = "-cam " + DRQUEUE_CAMERA
    else:
        camera_args=""

    if ("DRQUEUE_RESX" in globals()) and ("DRQUEUE_RESX" in globals()) and (int(DRQUEUE_RESX) > 0) and (int(DRQUEUE_RESY) > 0):
        res_args = "-x " + DRQUEUE_RESX + " -y " + DRQUEUE_RESY
    else:
        res_args = ""

    if ("DRQUEUE_FILEFORMAT" in globals()) and (DRQUEUE_FILEFORMAT != ""):
        format_args = "-of " + DRQUEUE_FILEFORMAT
    else:
        format_args = ""

    if ("DRQUEUE_RENDERDIR" in globals()) and (DRQUEUE_RENDERDIR != ""):
        os.chdir(DRQUEUE_RENDERDIR)

    # extra stuff for rendering single images in a couple of parts
    if DRQUEUE_RENDERTYPE == "single image":
        # calculate parts to render
        for line in open(DRQUEUE_SCENEFILE):
            if "resolution" in line:
                res_arr = line.split()
                if res_arr[0] == "resolution":
                    scene_height = res_arr[2]
                    scene_width = res_arr[1]

        part_height = scene_height / (DRQUEUE_ENDFRAME + 1)
        height_high = scene_height - (DRQUEUE_FRAME * part_height)
        height_low = height_high - part_height

        print("rendering dimensions: 0 " + height_low + " " + scene_width + " " + height_high)

        # generate frame filename
        for line in open(DRQUEUE_SCENEFILE):
            if "resolution" in line:
                if "." in line:
                    res_arr = line.split()
                    outputname = string.replace(res_arr[3], "\"", "")

        basename, extension = os.path.splitext(outputname)
        framename = basename + "_" + string.zfill(DRQUEUE_FRAME, 4) + "." + extension
        command = engine_path + " -window 0 " + str(height_low) + " " + str(scene_width) + " " + str(height_high) + " " + DRQUEUE_SCENEFILE + " -file_name " + framename 
    else:
        command = engine_path + " " + DRQUEUE_SCENEFILE + " -render " + str(DRQUEUE_FRAME) + " " + str(block)

    # log command line
    helper.log_write(command + "\n")

    # check scenefile
    helper.check_scenefile(DRQUEUE_SCENEFILE)

    # run renderer and wait for finish
    ret = helper.run_command(command)

    # return exit status to IPython
    return helper.return_to_ipython(ret)


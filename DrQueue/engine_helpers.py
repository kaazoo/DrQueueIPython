# -*- coding: utf-8 -*-

"""
DrQueue engine helpers submodule
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os, signal, subprocess, sys, platform
from time import strftime,localtime
import DrQueue
from computer import Computer as DrQueueComputer


def calc_block(frame, endframe, size):
    """Calculate block to render."""
    block = frame + size - 1
    if block > endframe:
    	  block = endframe
    return block

def replace_stdpath_with_driveletter(DRQUEUE_SCENEFILE, drive):
    """Replace DrQueue standard Unix path with specific Windows drive letter."""
    DRQUEUE_SCENEFILE = DRQUEUE_SCENEFILE.replace('/usr/local/drqueue', drive)
    DRQUEUE_SCENEFILE = DRQUEUE_SCENEFILE.replace('/', '\\')
    return DRQUEUE_SCENEFILE

def openlog(file):
    """Open logfile and write header."""
    logfile = open(file, "ab")
    logfile.write("Log started at " + strftime("%a, %d %b %Y %H:%M:%S", localtime()) + ".\n")
    logfile.write("Running on " + DrQueueComputer.get_hostname() + " under " + DrQueueComputer.get_os() + ".\n\n")
    return logfile

def check_scenefile(logfile, file):
    """Check if scenefile is existing."""
    if os.path.isfile(file) == False:
        message = "Scenefile was not found."
        logfile.write(message)
        logfile.close()
        raise ValueError(message)
        return False
        
def run_command(logfile, command):
    """Run command in shell."""
    try:
        p = subprocess.Popen(command, shell=True, stdout=logfile, stderr=subprocess.STDOUT)
    except OSError as (errno, strerror):
        message = "OSError({0}) while executing renderer: {1}\n".format(errno, strerror)
        logfile.write(message)
        logfile.close()
        raise OSError(message)
        return False
    p.wait()
    return p.returncode

def return_to_ipython(logfile, returncode):
    """Return exit status to IPython."""
    logfile.write("Exiting with status " + str(returncode) + ".\n\n")
    logfile.close()
    if returncode > 0:
        return False
    else:
        return True

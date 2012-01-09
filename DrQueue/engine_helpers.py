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
from .computer import Computer as DrQueueComputer


class Helper():
    """Object providing some helper methods for engines."""
    def __init__(self, logfile):
        self.logfile = self.openlog(logfile)

    def calc_block(self, frame, endframe, size):
        """Calculate block to render."""
        block = frame + size - 1
        if block > endframe:
        	  block = endframe
        return block

    def replace_stdpath_with_driveletter(self, path, drive):
        """Replace DrQueue standard Unix path with specific Windows drive letter."""
        path = path.replace('/usr/local/drqueue', drive)
        path = path.replace('/', '\\')
        return path

    def openlog(self, file):
        """Open logfile and write header."""
        logfile = open(file, "ab")
        logfile.write("Log started at " + strftime("%a, %d %b %Y %H:%M:%S", localtime()) + ".\n")
        logfile.write("Running on " + DrQueueComputer.get_hostname() + " under " + DrQueueComputer.get_os() + ".\n\n")
        return logfile

    def log_write(self, message):
        """Write message to logfile."""
        self.logfile.write(message)
        self.logfile.flush()
        return True

    def check_scenefile(self, scenefile):
        """Check if scenefile is existing."""
        if os.path.isfile(scenefile) == False:
            message = "Scenefile was not found."
            self.logfile.write(message)
            self.logfile.close()
            raise ValueError(message)
            return False

    def run_command(self, command):
        """Run command in shell."""
        try:
            p = subprocess.Popen(command, shell=True, stdout=self.logfile, stderr=subprocess.STDOUT)
        except OSError as e:
            errno, strerror = e.args
            message = "OSError({0}) while executing renderer: {1}\n".format(errno, strerror)
            self.logfile.write(message)
            self.logfile.close()
            raise OSError(message)
            return False
        p.wait()
        return p.returncode

    def return_to_ipython(self, returncode):
        """Return exit status to IPython."""
        self.logfile.write("Exiting with status " + str(returncode) + ".\n\n")
        self.logfile.close()
        if returncode > 0:
            return False
        else:
            return True


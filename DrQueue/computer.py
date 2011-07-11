# -*- coding: utf-8 -*-

"""
DrQueue Computer submodule
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os
import platform
import sys


class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable


class Computer(dict):
    """Subclass of dict for collecting Computer attribute values."""
    def __init__(self, engine_id):
        dict.__init__(self)
        comp = {
              'engine_id' : engine_id,
              'hostname' : Computer.get_hostname(),
              'arch' : Computer.get_arch(),
              'os' : Computer.get_os(),
              'proctype' : Computer.get_proctype(),
              'nbits' : Computer.get_nbits(),
              'procspeed' : None,
              'ncpus' : None,
              'ncorescpu' : None,
              'memory' : None,
             }
        self.update(comp)

    def get_hostname():
        """get hostname of computer"""
        return platform.node()
    get_hostname = Callable(get_hostname)

    def get_arch():
        """get hardware architecture of computer"""
        return platform.machine()
    get_arch = Callable(get_arch)

    def get_os():
        """get operating system name of computer"""
        osname = platform.system()
        osver = ""
        if osname == "Darwin":
            osname = "Mac OSX"
            osver = platform.mac_ver()[0]
        if osname == "Win32":
            osver = platform.win32_ver()[0] + " " + platform.win32_ver()[1]
        if osname == "Linux":
            osver = platform.linux_distribution()[0] + " " + platform.linux_distribution()[1]
        return osname + " " + osver
    get_os = Callable(get_os)

    def get_proctype():
        """get CPU type of computer"""
        return platform.processor()
    get_proctype = Callable(get_proctype)

    def get_nbits():
        """get bitness of computer"""
        if sys.maxsize > 2**32:
            return 64
        else:
            return 32
    get_nbits = Callable(get_nbits)

    def get_procspeed():
        """get CPU speed of computer"""
        return None
    get_procspeed = Callable(get_procspeed)

    def get_ncpus():
        """get number of CPUs of computer"""
        return None
    get_ncpus = Callable(get_ncpus)

    def get_ncorescpu():
        """get number of cores in CPU of computer"""
        return None
    get_ncorescpu = Callable(get_ncorescpu)

    def get_memory():
        """get number of CPUs of computer"""
        return None
    get_memory = Callable(get_memory)


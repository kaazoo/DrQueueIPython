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
import fileinput
from computer_pool import ComputerPool


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
              'procspeed' : Computer.get_procspeed(),
              'ncpus' : Computer.get_ncpus(),
              'ncorescpu' : Computer.get_ncorescpu(),
              'memory' : Computer.get_memory(),
              'load' : Computer.get_load()
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
        proctype = None
        if platform.system() == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Processor Name\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            proctype = output.split(":")[1].split("\n")[0].lstrip()
        if platform.system() == "Linux":
            proctype = platform.processor()
        if platform.system() == "Win32":
            proctype = platform.processor()
        return proctype
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
        speed = None
        if platform.system() == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Processor Speed\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            speed = output.split(":")[1].split("\n")[0].lstrip()
        if platform.system() == "Linux":
            for line in fileinput.input('/proc/cpuinfo'):
                if 'MHz' in line:
                    speed = line.split(':')[1].strip() + " " + "MHz"
        if platform.system() == "Win32":
            import _winreg
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            speed, type = _winreg.QueryValueEx(key, "~MHz")
            speed = speed + " " + "MHz"
        return speed
    get_procspeed = Callable(get_procspeed)

    def get_ncpus():
        """get number of CPUs of computer"""
        ncpus = None
        if platform.system() == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Number Of Processors\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            ncpus = int(output.split(":")[1].split("\n")[0])
        if platform.system() == "Linux":
            phyids = []
            for line in fileinput.input('/proc/cpuinfo'):
                if 'physical id' in line:
                    phyids.append(line)
            uniq = set(phyids)
            ncpus = len(uniq)
        if platform.system() == "Win32":
            ncpus = None
        return ncpus
    get_ncpus = Callable(get_ncpus)

    def get_ncorescpu():
        """get number of cores in CPU of computer"""
        ncorescpu = None
        if platform.system() == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Total Number Of Cores\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            total_cores = output.split(":")[1].split("\n")[0]
            ncorescpu = int(total_cores) / Computer.get_ncpus()
        if platform.system() == "Linux":
            phyids = [] 
            for line in fileinput.input('/proc/cpuinfo'):
                if 'physical id' in line:
                    phyids.append(line)
            uniq = set(phyids)
            ncorescpu = len(phyids) / len(uniq)
        if platform.system() == "Win32":
            ncorescpu = None
        return ncorescpu
    get_ncorescpu = Callable(get_ncorescpu)

    def get_memory():
        """get amount of memory of computer"""
        memory = None
        if platform.system() == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Memory\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            memory = output.split(":")[1].split("\n")[0].lstrip()
        if platform.system() == "Linux":
            for line in fileinput.input('/proc/meminfo'):
                if 'MemTotal' in line:
                    memory = line.split(':')[1].strip().split(' ')[0].strip()
                    memory = str(round(float(memory)/1024/1024, 2)) + " " + "GB"
        if platform.system() == "Win32":
            memory = None
        return memory
    get_memory = Callable(get_memory)


    def get_load():
        """get load of computer"""
        load = None
        if (platform.system() == "Darwin") or (platform.system() == "Linux"):
            loads = os.getloadavg()
            load = str(round(loads[0],2)) + " " + str(round(loads[1], 2)) + " " + str(round(loads[2], 2))
        if platform.system() == "Win32":
            load = None
        return load
    get_load = Callable(get_load)


    def get_pools(computer):
        """list pools to which computer belongs"""
        engine_pools = []
        pools = ComputerPool.query_pool_list()
        for pool in pools:
            if type(pool['engine_ids']).__name__ == 'list':
                if computer in pool['engine_ids']:
                    engine_pools.append(pool['name'])
        return engine_pools
    get_pools = Callable(get_pools)


    def set_pools(computer, pool_list):
        """add computer to list of pools"""
        if type(pool_list).__name__ != 'list':
            raise ValueError("argument is not of type list")
            return False
        # prepare list of pools of which computer should be taken out
        old_pools = Computer.get_pools(computer)
        old_pools_to_delete = old_pools
        for pool_name in pool_list:
            # remove name from list
            if pool_name in old_pools_to_delete:
                old_pools_to_delete.remove(pool_name)
            # look if pool is already existing
            pool = ComputerPool.query_pool_by_name(pool_name)
            # create new pool if not existing
            if pool == None:
                pool = ComputerPool(pool_name, [computer])
                # store information in db
                ComputerPool.store_db(pool)
            # pool is already existing
            else:
                # look if computer is already in pool
                if computer in pool['engine_ids']:
                    print("Computer %i is already in pool %s" % (computer, pool_name))
                else:
                    # add computer to pool
                    print("Computer %i added to pool %s" % (computer, pool_name))
                    pool['engine_ids'].append(computer)
                # update information in db
                ComputerPool.update_db(pool)
        # work on list of old pools
        for pool_name in old_pools_to_delete:
            pool = ComputerPool.query_pool_by_name(pool_name)
            if pool != None:
                print("Computer %i removed from pool %s" % (computer, pool_name))
                pool['engine_ids'].remove(computer)
            # update information in db
            ComputerPool.update_db(pool)
        return True
    set_pools = Callable(set_pools)


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
from .computer_pool import ComputerPool


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
        if osname in ["Windows", "Win32"]:
            osver = platform.win32_ver()[0] + " " + platform.win32_ver()[1]
        if osname == "Linux":
            osver = platform.linux_distribution()[0] + " " + platform.linux_distribution()[1]
        return osname + " " + osver
    get_os = Callable(get_os)

    def get_proctype():
        """get CPU type of computer"""
        osname = platform.system()
        proctype = ""
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Processor Name\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            proctype = output.split(":")[1].split("\n")[0].lstrip()
        if osname == ["Linux", "Windows", "Win32"]:
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
        osname = platform.system()
        speed = ""
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Processor Speed\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            speed = output.split(":")[1].split("\n")[0].lstrip()
        if osname == "Linux":
            for line in fileinput.input('/proc/cpuinfo'):
                if 'MHz' in line:
                    speed = line.split(':')[1].strip() + " MHz"
        if osname in ["Windows", "Win32"]:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            speed, type = winreg.QueryValueEx(key, "~MHz")
            speed = str(speed) + " MHz"
        return speed
    get_procspeed = Callable(get_procspeed)

    def get_ncpus():
        """get number of CPUs of computer"""
        osname = platform.system()
        ncpus = 0
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Number Of Processors\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            ncpus = int(output.split(":")[1].split("\n")[0])
        if osname == "Linux":
            phyids = []
            for line in fileinput.input('/proc/cpuinfo'):
                if 'physical id' in line:
                    phyids.append(line)
            uniq = set(phyids)
            ncpus = len(uniq)
        if osname in ["Windows", "Win32"]:
            ncpus = int(os.environ['NUMBER_OF_PROCESSORS'])
        return ncpus
    get_ncpus = Callable(get_ncpus)

    def get_ncorescpu():
        """get number of cores in CPU of computer"""
        osname = platform.system()
        ncorescpu = 0
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Total Number Of Cores\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            total_cores = output.split(":")[1].split("\n")[0]
            ncorescpu = int(total_cores) / Computer.get_ncpus()
        if osname == "Linux":
            phyids = [] 
            for line in fileinput.input('/proc/cpuinfo'):
                if 'physical id' in line:
                    phyids.append(line)
            uniq = set(phyids)
            ncorescpu = len(phyids) / len(uniq)
        if osname in ["Windows", "Win32"]:
            ncorescpu = 1
        return ncorescpu
    get_ncorescpu = Callable(get_ncorescpu)

    def get_memory():
        """get amount of memory of computer in GB"""
        osname = platform.system()
        memory = 0.0
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Memory\""], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            memory = float(output.split(":")[1].split("\n")[0].lstrip().split(" ")[0])
        if osname == "Linux":
            for line in fileinput.input('/proc/meminfo'):
                if 'MemTotal' in line:
                    memory = line.split(':')[1].strip().split(' ')[0].strip()
                    memory = round(float(memory)/1024/1024, 2)
        if osname in ["Windows", "Win32"]:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            c_ulong = ctypes.c_ulong
            class MEMORYSTATUS(ctypes.Structure):
                _fields_ = [
                    ('dwLength', c_ulong),
                    ('dwMemoryLoad', c_ulong),
                    ('dwTotalPhys', c_ulong),
                    ('dwAvailPhys', c_ulong),
                    ('dwTotalPageFile', c_ulong),
                    ('dwAvailPageFile', c_ulong),
                    ('dwTotalVirtual', c_ulong),
                    ('dwAvailVirtual', c_ulong)
                ]
            memoryStatus = MEMORYSTATUS()
            memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUS)
            kernel32.GlobalMemoryStatus(ctypes.byref(memoryStatus))
            mem = memoryStatus.dwTotalPhys / (1024*1024)
            mem = mem / 1000
            memory = float(mem)
        return memory
    get_memory = Callable(get_memory)


    def get_load():
        """get load of computer"""
        osname = platform.system()
        load = ""
        if osname in ["Darwin", "Linux"]:
            loads = os.getloadavg()
            load = str(round(loads[0],2)) + " " + str(round(loads[1], 2)) + " " + str(round(loads[2], 2))
        if osname in ["Windows", "Win32"]:
            cmd = "WMIC CPU GET LoadPercentage "
            response = os.popen(cmd + ' 2>&1','r').read().strip().split("\r\n")
            load = response[1]
        return load
    get_load = Callable(get_load)


    def get_pools(computer_name):
        """list pools to which computer belongs"""
        engine_pools = []
        pools = ComputerPool.query_pool_list()
        for pool in pools:
            if ('engine_names' in pool) and (type(pool['engine_names']).__name__ == 'list'):
                if computer_name in pool['engine_names']:
                    engine_pools.append(pool['name'])
        return engine_pools
    get_pools = Callable(get_pools)


    def set_pools(computer_name, pool_list):
        """add computer to list of pools"""
        if type(pool_list).__name__ != 'list':
            raise ValueError("argument is not of type list")
            return False
        # prepare list of pools of which computer should be taken out
        old_pools = Computer.get_pools(computer_name)
        old_pools_to_delete = old_pools
        for pool_name in pool_list:
            # remove name from list
            if pool_name in old_pools_to_delete:
                old_pools_to_delete.remove(pool_name)
            # look if pool is already existing
            pool = ComputerPool.query_pool_by_name(pool_name)
            # create new pool if not existing
            if pool == None:
                pool = ComputerPool(pool_name, [computer_name])
                # store information in db
                ComputerPool.store_db(pool)
            # pool is already existing
            else:
                # look if computer is already in pool
                if computer_name in pool['engine_names']:
                    print("Computer \"%s\" is already in pool \"%s\"" % (computer_name, pool_name))
                else:
                    # add computer to pool
                    print("Computer \"%s\" added to pool \"%s\"" % (computer_name, pool_name))
                    pool['engine_names'].append(computer_name)
                # update information in db
                ComputerPool.update_db(pool)
        # work on list of old pools
        for pool_name in old_pools_to_delete:
            pool = ComputerPool.query_pool_by_name(pool_name)
            if pool != None:
                print("Computer \"%s\" removed from pool \"%s\"" % (computer_name, pool_name))
                pool['engine_names'].remove(computer_name)
            # update information in db
            ComputerPool.update_db(pool)
        return True
    set_pools = Callable(set_pools)


    def query_db(engine_id):
        import pymongo
        """query computer information from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MASTER'))
        db = connection['ipythondb']
        computers = db['drqueue_computers']
        computer = computers.find_one({"engine_id" : engine_id})
        return computer
    query_db = Callable(query_db)


    def store_db(engine):
        import pymongo
        """store computer information in MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MASTER'))
        db = connection['ipythondb']
        computers = db['drqueue_computers']
        # remove old entry
        computers.remove({"engine_id" : engine['engine_id']})
        computer_id = computers.insert(engine)
        engine['_id'] = str(engine['_id'])
        return computer_id
    store_db = Callable(store_db)


    def delete_from_db(engine_id):
        import pymongo
        import bson
        """delete comouter information from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MASTER'))
        db = connection['ipythondb']
        computers = db['drqueue_computers']
        computers.remove({"engine_id" : engine_id})
        return True
    delete_from_db = Callable(delete_from_db)




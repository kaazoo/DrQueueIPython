# -*- coding: utf-8 -*-

"""
DrQueue Computer submodule
Copyright (C) 2011,2012 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os
import platform
import sys
import fileinput
import socket


class Computer(dict):
    """Subclass of dict for collecting Computer attribute values."""
    def __init__(self):
        dict.__init__(self)
        comp = {
              'engine_id' : None,
              'created_at' : None,
              'hostname' : Computer.get_hostname(),
              'arch' : Computer.get_arch(),
              'os' : Computer.get_os(),
              'proctype' : Computer.get_proctype(),
              'nbits' : Computer.get_nbits(),
              'procspeed' : Computer.get_procspeed(),
              'ncpus' : Computer.get_ncpus(),
              'ncorescpu' : Computer.get_ncorescpu(),
              'memory' : Computer.get_memory(),
              'load' : Computer.get_load(),
              'address' : Computer.get_address(),
              'pools' : Computer.get_pools()
        }
        self.update(comp)


    @staticmethod
    def get_hostname():
        """get hostname of computer"""
        return platform.node()


    @staticmethod
    def get_arch():
        """get hardware architecture of computer"""
        return platform.machine()


    @staticmethod
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


    @staticmethod
    def get_proctype():
        """get CPU type of computer"""
        osname = platform.system()
        proctype = ""
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Processor Name\" | cut -d \":\" -f2"], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            proctype = output.lstrip()
        if osname == ["Linux", "Windows", "Win32"]:
            proctype = platform.processor()
        return proctype


    @staticmethod
    def get_nbits():
        """get bitness of computer"""
        if sys.maxsize > 2**32:
            return 64
        else:
            return 32


    @staticmethod
    def get_procspeed():
        """get CPU speed of computer"""
        osname = platform.system()
        speed = ""
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Processor Speed\" | cut -d \":\" -f2"], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            speed = output.lstrip()
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


    @staticmethod
    def get_ncpus():
        """get number of CPUs of computer"""
        osname = platform.system()
        ncpus = 0
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Number Of Processors\" | cut -d \":\" -f2"], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            ncpus = int(output.lstrip())
        if osname == "Linux":
            phyids = []
            for line in fileinput.input('/proc/cpuinfo'):
                if 'physical id' in line:
                    phyids.append(line)
            uniq = set(phyids)
            # TODO: fix this for virtual machines
            if len(uniq) == 0:
                ncpus = 1
            else:
                ncpus = len(uniq)
        if osname in ["Windows", "Win32"]:
            ncpus = int(os.environ['NUMBER_OF_PROCESSORS'])
        return ncpus


    @staticmethod
    def get_ncorescpu():
        """get number of cores in CPU of computer"""
        osname = platform.system()
        ncorescpu = 0
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Total Number Of Cores\" | cut -d \":\" -f2"], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            total_cores = int(output.lstrip())
            ncorescpu = int(total_cores) / Computer.get_ncpus()
        if osname == "Linux":
            phyids = [] 
            for line in fileinput.input('/proc/cpuinfo'):
                if 'physical id' in line:
                    phyids.append(line)
            uniq = set(phyids)
            # TODO: fix this for virtual machines
            if len(uniq) == 0:
                ncorescpu = 1
            else:
                ncorescpu = len(phyids) / len(uniq)
        if osname in ["Windows", "Win32"]:
            ncorescpu = 1
        return ncorescpu


    @staticmethod
    def get_memory():
        """get amount of memory of computer in GB"""
        osname = platform.system()
        memory = 0.0
        if osname == "Darwin":
            import subprocess
            proc = subprocess.Popen(["system_profiler SPHardwareDataType | grep \"Memory\" | cut -d \":\" -f2 | cut -d \" \" -f2"], shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            memory = float(output)
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


    @staticmethod
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


    @staticmethod
    def get_pools():
        """list pools to which computer belongs"""
        if "DRQUEUE_POOL" in os.environ:
            engine_pools = os.environ["DRQUEUE_POOL"].split(",")
        else:
            engine_pools = []
        return engine_pools


    @staticmethod
    def get_address():
        """Find out external IP address of computer."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((os.environ["DRQUEUE_MASTER"], 1))
        ex_ip = s.getsockname()[0]
        return ex_ip


    @staticmethod
    def query_all():
        import pymongo
        """query all computer entries from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MASTER'))
        db = connection['ipythondb']
        computers = db['drqueue_computers']
        entries = []
        for entry in computers.find():
            entries.append(entry['engine_id'])
        return entries


    @staticmethod
    def query_db_by_engine_id(engine_id):
        import pymongo
        """query computer information from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MASTER'))
        db = connection['ipythondb']
        computers = db['drqueue_computers']
        computer = computers.find_one({"engine_id" : engine_id})
        return computer


    @staticmethod
    def query_db_by_hostname(hostname):
        import pymongo
        """query computer information from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MASTER'))
        db = connection['ipythondb']
        computers = db['drqueue_computers']
        computer = computers.find_one({"hostname" : hostname})
        return computer


    @staticmethod
    def store_db(engine):
        import pymongo
        """store computer information in MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MASTER'))
        db = connection['ipythondb']
        computers = db['drqueue_computers']
        # remove old entry by hostname
        computers.remove({"hostname" : engine['hostname']})
        computer_id = computers.insert(engine)
        engine['_id'] = str(engine['_id'])
        return computer_id


    @staticmethod
    def delete_from_db_by_engine_id(engine_id):
        import pymongo
        import bson
        """delete comouter information from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MASTER'))
        db = connection['ipythondb']
        computers = db['drqueue_computers']
        ret = computers.remove({"engine_id" : engine_id})
        return ret


    @staticmethod
    def delete_from_db_by_hostname(hostname):
        import pymongo
        import bson
        """delete comouter information from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MASTER'))
        db = connection['ipythondb']
        computers = db['drqueue_computers']
        ret = computers.remove({"hostname" : hostname})
        return ret


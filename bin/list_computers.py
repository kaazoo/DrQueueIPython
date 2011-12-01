# -*- coding: utf-8 -*-

"""
List information about connected computers
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

from DrQueue import Client

c = Client()

cache_time = 60

for comp_id in c.ip_client.ids:
    print("Engine " + str(comp_id) + ":")
    comp = c.identify_computer(comp_id, cache_time)
    print(" hostname: " + comp['hostname'])
    print(" arch: " + comp['arch'])
    print(" os: " + comp['os'])
    print(" proctype: " + comp['proctype'])
    print(" nbits: " + str(comp['nbits']))
    print(" procspeed: " + comp['procspeed'])
    print(" ncpus: " + str(comp['ncpus']))
    print(" ncorescpu: " + str(comp['ncorescpu']))
    print(" memory: " + str(comp['memory']) + " GB")
    print(" load: " + comp['load'])
    status = c.ip_client.queue_status(comp_id, verbose=True)
    print(" status:")
    print("  in queue: " + str(status['queue']))
    print("  completed: " + str(status['completed']))
    print("  tasks: " + str(status['tasks']))



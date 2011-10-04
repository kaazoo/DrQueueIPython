# -*- coding: utf-8 -*-

"""
Control connected computers
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

from optparse import OptionParser
import os
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient
from DrQueue import Computer as DrQueueComputer
from DrQueue import ComputerPool as DrQueueComputerPool


def main():
    # parse arguments
    parser = OptionParser()
    parser.usage = "%prog [options] -i id"
    parser.add_option("-i", "--id ",
                      dest="id", default=None, help="id of computer")
    parser.add_option("-a", "--all ",
                      action="store_true", dest="all", default=False, help="use all computers")
    parser.add_option("-s", "--shutdown",
                      action="store_true", dest="shutdown", default=False, help="shutdown computer")
    parser.add_option("-p", "--pools",
                      dest="pools", default=None, help="add computer to one or more pools")
    parser.add_option("--info",
                      action="store_true", dest="info", default=False, help="show information about computer")
    parser.add_option("-t", "--status",
                      action="store_true", dest="status", default=False, help="show status of computer")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False, help="verbose output")
    (options, args) = parser.parse_args()

    # initialize DrQueue client
    client = DrQueueClient()

    cache_time = 60

    # engines to work on
    if options.id != None:
        computers = []
        computers.append(int(options.id))
    if options.all == True:
        computers = client.ip_client.ids

    # run specified action
    if options.shutdown:
        for computer in computers:
            client.engine_stop(computer)
        print("Computer %s has been shut down." % str(computers))
        return True
    if options.pools:
        for computer in computers:
            comp = client.identify_computer(computer, cache_time)
            DrQueueComputer.set_pools(comp['hostname'], options.pools.split(","))
            print("Computer %i has been added to pools %s." % (computer, options.pools.split(",")))
        return True
    if options.info:
        for computer in computers:
            print("Engine " + str(computer) + ":")
            comp = client.identify_computer(computer, cache_time)
            print(" hostname: " + comp['hostname'])
            print(" arch: " + comp['arch'])
            print(" os: " + comp['os'])
            print(" nbits: " + str(comp['nbits']))
            print(" procspeed: " + comp['procspeed'])
            print(" ncpus: " + str(comp['ncpus']))
            print(" ncorescpu: " + str(comp['ncorescpu']))
            print(" memory: " + str(comp['memory']))
            print(" load: " + comp['load'])
            print(" pools: " + str(DrQueueComputer.get_pools(comp['hostname'])) + "\n")
        return True
    if options.status:
        for computer in computers:
            print("Engine " + str(computer) + ":")
            status = client.ip_client.queue_status(computer, verbose=True)
            print(" status:")
            print("  in queue: " + str(status['queue']))
            print("  completed: " + str(status['completed']))
            print("  tasks: " + str(status['tasks']))
        return True

if __name__ == "__main__":
    main()



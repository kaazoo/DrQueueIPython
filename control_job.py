# -*- coding: utf-8 -*-

"""
Control existing jobs
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os, sys
from optparse import OptionParser
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient


def main():
    # parse arguments
    parser = OptionParser()
    parser.usage = "%prog [options] -n name"
    parser.add_option("-n", "--name ",
                      dest="name", help="name of job")
    parser.add_option("-i", "--id ",
                      dest="id", default=0, help="id of job")
    parser.add_option("-s", "--stop",
                      action="store_true", dest="stop", default=False, help="stop the job")
    parser.add_option("-k", "--kill",
                      action="store_true", dest="kill", default=False, help="stop the job (be careful, running tasks will be killed)")
    parser.add_option("-d", "--delete",
                      action="store_true", dest="delete", default=False, help="delete the job (be careful, no confirmation asked)")
    parser.add_option("-c", "--continue",
                      action="store_true", dest="cont", default=False, help="continue a previously stopped job")
    parser.add_option("-r", "--rerun",
                      action="store_true", dest="rerun", default=False, help="rerun job")
    parser.add_option("-t", "--status",
                      action="store_true", dest="status", default=False, help="show the status of the job")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False, help="verbose output")
    (options, args) = parser.parse_args()

    # initialize DrQueue client
    client = DrQueueClient()

    # get job information
    if options.id == 0:
        job = DrQueueJob.query_job_by_name(options.name)
        if job == None:
            print("Specified job does not exist.")
            sys.exit(1)
        job_id = job['_id']
        job_name = options.name
    else:
        job_id = options.id
        job = DrQueueJob.query_db(job_id)
        if job == None:
            print("Specified job does not exist.")
            sys.exit(1)
        job_name = job['name']

    # run specified action on job
    if options.stop:
        client.job_stop(job_id)
        print("Job %s has been stopped." % job_name)
        return
    if options.kill:
        client.job_kill(job_id)
        print("Job %s has been killed." % job_name)
        return
    if options.delete:
        client.job_delete(job_id)
        print("Job %s has been deleted." % job_name)
        return
    if options.cont:
        client.job_continue(job_id)
        print("Job %s is running again." % job_name)
        return
    if options.rerun:
        client.job_rerun(job_id)
        print("Job %s is running another time." % job_name)
        return
    if options.status:
        status = client.job_status(job_id)
        print("The status of job %s is \"%s\"" % (job_name, status))
        return

if __name__ == "__main__":
    main()



# -*- coding: utf-8 -*-

"""
Control existing jobs
Copyright (C) 2011-2013 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os, sys
import argparse
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient


def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name ",
                      dest="name", default="", help="name of job")
    parser.add_argument("-i", "--id ",
                      dest="id", default=0, help="id of job ('ALL' for all jobs)")
    parser.add_argument("--tid ",
                      dest="tid", default=0, help="id of task ('ALL' for all tasks)")
    parser.add_argument("-s", "--stop",
                      action="store_true", dest="stop", default=False, help="stop the job")
    parser.add_argument("-k", "--kill",
                      action="store_true", dest="kill", default=False, help="stop the job (be careful, running tasks will be killed)")
    parser.add_argument("-d", "--delete",
                      action="store_true", dest="delete", default=False, help="delete the job (be careful, no confirmation asked)")
    parser.add_argument("-c", "--continue",
                      action="store_true", dest="cont", default=False, help="continue a previously stopped job")
    parser.add_argument("-r", "--rerun",
                      action="store_true", dest="rerun", default=False, help="rerun job with ID 'id'")
    parser.add_argument("-R", "--rerun_task",
                      action="store_true", dest="rerun_task", default=False, help="rerun task with ID 'tid' of job identified by ID 'id' or NAME 'n'")
    parser.add_argument("-F", "--rerun_interrupted_tasks",
                      action="store_true", dest="rerun_interrupted_tasks", default=False, help="rerun interrupted tasks")
    parser.add_argument("-t", "--status",
                      action="store_true", dest="status", default=False, help="show the status of the job")
    parser.add_argument("-v", "--verbose",
                      action="store_true", dest="verbose", default=False, help="verbose output")
    args = parser.parse_args()


    # initialize DrQueue client
    client = DrQueueClient()

    # get job information by name
    if (args.id == 0) and (args.name != ""):
        jobs = []
        job = client.query_job_by_name(args.name)
        if job == None:
            print("Specified job does not exist.")
            sys.exit(1)
        jobs.append(job)
    # get job information by id
    elif (args.id != 0) and (args.name == ""):
        if args.id == "ALL":
            jobs = client.query_job_list()
        else:
            jobs = []
            job = client.query_job_by_id(args.id)
            if job == None:
                print("Specified job does not exist.")
                sys.exit(1)
            jobs.append(job)
    # id and name are missing
    else:
        parser.print_help()
        sys.exit(1)

    # work on task id
    if args.tid != 0:
        if args.rerun_task:
            client.task_rerun(args.tid)
            print("Task %s of job %s is running another time." % (args.tid, jobs[0]['name']))
            return

    # run specified action on job(s)
    for job in jobs:
        if args.stop:
            client.job_stop(job['_id'])
            print("Job %s has been stopped.\n" % job['name'])
        if args.kill:
            client.job_kill(job['_id'])
            print("Job %s has been killed.\n" % job['name'])
        if args.delete:
            client.job_delete(job['_id'])
            print("Job %s has been deleted.\n" % job['name'])
        if args.cont:
            client.job_continue(job['_id'])
            print("Job %s is running again.\n" % job['name'])
        if args.rerun:
            client.job_rerun(job['_id'])
            print("Job %s is running another time.\n" % job['name'])
        if args.rerun_interrupted_tasks:
            client.job_rerun_interrupted_tasks(job['_id'])
            print("Interrupted tasks of job %s are running another time.\n" % job['name'])
        if args.status:
            status = client.job_status(job['_id'])
            print("The status of job %s is \"%s\"\n" % (job['name'], status))
    return

if __name__ == "__main__":
    main()



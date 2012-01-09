# -*- coding: utf-8 -*-

"""
Create new job
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

from optparse import OptionParser
import os
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient
import getpass


def main():
    # parse arguments
    parser = OptionParser()
    parser.usage = "%prog [options] -n name -r renderer -f scenefile"
    parser.add_option("-s", "--startframe",
                      dest="startframe", default=1, help="first frame")
    parser.add_option("-e", "--endframe",
                      dest="endframe", default=1, help="last frame")
    parser.add_option("-b", "--blocksize",
                      dest="blocksize", default=1, help="size of block")
    parser.add_option("-n", "--name",
                      dest="name", default=None, help="name of job")
    parser.add_option("-r", "--renderer",
                      dest="renderer", help="render type (maya|blender|mentalray)")
    parser.add_option("-f", "--scenefile",
                      dest="scenefile", default=None, help="path to scenefile")
    parser.add_option("-p", "--pool",
                      dest="pool", default=None, help="pool of computers")
    parser.add_option("-o", "--options",
                      dest="options", default="{}", help="specific options for renderer as Python dict")
    parser.add_option("--retries",
                      dest="retries", default=1, help="number of retries for every task")
    parser.add_option("--owner",
                      dest="owner", default=getpass.getuser(), help="Owner of job. Default is current username.")
    parser.add_option("--os",
                      dest="os", default=None, help="Operating system.")
    parser.add_option("--minram",
                      dest="minram", default=0, help="Minimal RAM in GB.")
    parser.add_option("--mincores",
                      dest="mincores", default=0, help="Minimal CPU cores.")
    parser.add_option("--send-email",
                      action="store_true", dest="send_email", default=False, help="Send notification email when job is finished.")
    parser.add_option("--email-recipients",
                      dest="email_recipients", default=None, help="Recipients for notification email.")
    parser.add_option("-w", "--wait",
                      action="store_true", dest="wait", default=False, help="wait for job to finish")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False, help="verbose output")
    (options, args) = parser.parse_args()

    # initialize DrQueue client
    client = DrQueueClient()

    # set limits
    limits = dict()
    limits['pool_name'] = options.pool
    limits['os'] = options.os
    limits['minram'] = int(options.minram)
    limits['mincores'] = int(options.mincores)

    options_var = eval(options.options)
    options_var['send_email'] = options.send_email
    options_var['email_recipients'] = options.email_recipients

    # initialize DrQueue job
    job = DrQueueJob(options.name, int(options.startframe), int(options.endframe), int(options.blocksize), options.renderer, options.scenefile, options.retries, options.owner, options_var, "send_job.py", limits)

    # run job with client
    try:
        client.job_run(job)
    except ValueError:
        print("One of your the specified values produced an error:")
        raise
        exit(1)

    # tasks which have been created
    tasks = client.query_task_list(job['_id'])

    # wait for all tasks of job to finish
    if options.wait:
        if (tasks == []) and (client.query_engine_list() == []):
            print("Tasks have been sent but no render node is running at the moment.")
            exit(0)

        for task in tasks:
            ar = client.task_wait(task['msg_id'])
            # add some verbose output
            if options.verbose:
                cpl = ar.metadata.completed
                msg_id = ar.metadata.msg_id
                status = ar.status
                engine_id = ar.metadata.engine_id
                print("Task %s finished with status '%s' on engine %i at %i-%02i-%02i %02i:%02i:%02i." % (msg_id, status, engine_id, cpl.year, cpl.month, cpl.day, cpl.hour, cpl.minute, cpl.second))
                if ar.pyerr != None:
                    print(ar.pyerr)
        print("Job %s finished." % job['name'])

if __name__ == "__main__":
    main()



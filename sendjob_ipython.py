# -*- coding: utf-8 -*-

from optparse import OptionParser
import os
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient


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
    parser.add_option("-o", "--options",
                      dest="options", default="{}", help="specific options for renderer as Python dict")
    parser.add_option("-w", "--wait",
                      action="store_true", dest="wait", default=False, help="wait for job to finish")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False, help="verbose output")
    (options, args) = parser.parse_args()

    # initialize DrQueue client
    client = DrQueueClient()

    # initialize DrQueue job
    job = DrQueueJob(options.name, int(options.startframe), int(options.endframe), int(options.blocksize), options.renderer, options.scenefile, eval(options.options))

    # run job with client
    client.job_run(job)

    # tasks which have been created
    tasks = client.query_tasks_of_job(job['name'])

    # wait for all tasks of job to finish
    if options.wait:
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



# -*- coding: utf-8 -*-

from optparse import OptionParser
import os
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient


def main():
    # parse arguments
    parser = OptionParser()
    parser.usage = "%prog [options] -r renderer -f scenefile"
    parser.add_option("-s", "--startframe", dest="startframe", default=1,
                      help="first frame")
    parser.add_option("-e", "--endframe", dest="endframe", default=1,
                      help="last frame")
    parser.add_option("-b", "--blocksize", dest="blocksize", default=1,
                      help="size of block")
    parser.add_option("-f", "--scenefile", dest="scenefile", default=1,
                      help="path to scenefile")
    parser.add_option("-r", "--renderer", dest="renderer",
                      help="render type (maya|blender|mentalray)")
    parser.add_option("-w", "--wait", action="store_true", dest="wait", default=False,
                      help="wait for job to finish")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="verbose output")
    (options, args) = parser.parse_args()

    # initialize DrQueue client
    client = DrQueueClient()

    # initialize DrQueue job
    job = DrQueueJob(int(options.startframe), int(options.blocksize), int(options.endframe), options.scenefile, options.renderer)

    # run job with client
    client.run_job(job)

    # wait for the job to finish
    if options.wait:
        # wait for the tasks to finish
        if options.verbose:
            for task in job['tasks']:
                task.wait()
                cpl = task.metadata.completed
                msg_id = task.metadata.msg_id
                status = task.status
                engine_id = task.metadata.engine_id
                print("Task %s finished with status '%s' on engine %i at %i-%02i-%02i %02i:%02i:%02i." % (msg_id, status, engine_id, cpl.year, cpl.month, cpl.day, cpl.hour, cpl.minute, cpl.second))
                if task.pyerr != None:
                    print(task.pyerr)
        job['dummy_task'].wait()
        cpl = job['dummy_task'].metadata.completed
        msg_id = job['dummy_task'].metadata.msg_id
        status = job['dummy_task'].status
        print("Job %s finished with status '%s' at %i-%02i-%02i %02i:%02i:%02i." % (msg_id, status, cpl.year, cpl.month, cpl.day, cpl.hour, cpl.minute, cpl.second))


if __name__ == "__main__":
    main()



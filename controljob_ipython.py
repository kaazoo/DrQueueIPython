# -*- coding: utf-8 -*-

from optparse import OptionParser
import os
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient


def main():
    # parse arguments
    parser = OptionParser()
    parser.usage = "%prog [options] -n name"
    parser.add_option("-n", "--name ",
                      dest="name", help="name of job")
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

    # run specified action on job
    if options.stop:
        client.job_stop(options.name)
        print("Job %s has been stopped." % options.name)
        return
    if options.kill:
        client.job_kill(options.name)
        print("Job %s has been killed." % options.name)
        return
    if options.delete:
        client.job_delete(options.name)
        print("Job %s has been deleted." % options.name)
        return
    if options.cont:
        client.job_continue(options.name)
        print("Job %s is running again." % options.name)
        return
    if options.rerun:
        client.job_rerun(options.name)
        print("Job %s is running another time." % options.name)
        return
    if options.status:
        status = client.job_status(options.name)
        print("The status of job %s is \"%s\"" % (options.name, status))
        return

if __name__ == "__main__":
    main()



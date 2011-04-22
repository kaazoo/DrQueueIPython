# -*- coding: utf-8 -*-

from optparse import OptionParser
import os
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient


def main():
    # parse arguments
    parser = OptionParser()
    parser.usage = "%prog [options] -j job_id"
    parser.add_option("-j", "--job_id ", 
                      dest="job_id", help="job id")
    parser.add_option("-s", "--stop", 
                      action="store_true", dest="stop", default=False, help="stop the job")
    parser.add_option("-k", "--kill", 
                      action="store_true", dest="kill", default=False, help="stop the job (be careful, running tasks will be killed)")
    parser.add_option("-d", "--delete", 
                      action="store_true", dest="delete", default=False, help="delete the job (be careful, no confirmation asked)")
    parser.add_option("-c", "--continue", 
                      action="store_true", dest="cont", default=False, help="continue a previously stopped job")
    parser.add_option("-t", "--status", 
                      action="store_true", dest="status", default=False, help="show the status of the job")
    parser.add_option("-v", "--verbose", 
                      action="store_true", dest="verbose", default=False, help="verbose output")
    (options, args) = parser.parse_args()

    # initialize DrQueue client
    client = DrQueueClient()

    # run specified action on job
    if options.stop:
        client.job_stop(options.job_id)
        print("Job %s has been stopped." % options.job_id)
        return
    if options.kill:
        client.job_kill(options.job_id)
        print("Job %s has been killed." % options.job_id)
        return
    if options.delete:
        client.job_delete(options.job_id)
        print("Job %s has been deleted." % options.job_id)
        return
    if options.cont:
        client.job_continue(options.job_id)
        print("Job %s is running again." % options.job_id)
        return     
    if options.status:
        status = client.job_status(options.job_id)
        print("The status of job %s is \"%s\"" % (options.job_id, status))
        return

if __name__ == "__main__":
    main()



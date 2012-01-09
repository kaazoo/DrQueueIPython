# -*- coding: utf-8 -*-

"""
List information about existing jobs
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import string
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient


def main():
    # initialize DrQueue client
    client = DrQueueClient()
    # fetch a list of all jobs
    jobs = client.query_job_list()
        
    # walk through tasks of every job
    for job in jobs:
        tasks = client.query_task_list(job['_id'])
        meantime, time_left, finish_time = client.job_estimated_finish_time(job['_id'])
        
        print("\nJob \"%s\" (ID: %s):" % (job['name'], job['_id']))
        print("Overall status: " + client.job_status(job['_id']))
        print("Submit time: "+ str(job['submit_time']))
        if job['requeue_time'] != False:
            print("Requeue time: "+ str(job['requeue_time']))
        print("Time per task: " + str(meantime))
        if client.query_job_tasks_left(job['_id']) > 0:
            print("Time left: " + str(time_left))
            print("Estimated finish time: " + str(finish_time))
        else:
            print("Finish time: " + str(finish_time))
        print("Task id                                 status    owner       completed at")
        
        for task in tasks:
            tmsg_id = task['msg_id']
            theader = task['header']
            username = theader['username']
        
            if task['completed'] == None:
                status = "pending"
                print("%s   %s  %s" % (tmsg_id, string.ljust(status, 8), string.ljust(username, 10)))
            else:
                result_header = task['result_header']
                result_content = task['result_content']
                status = result_header['status']
                cpl = task['completed']
                print("%s   %s  %s  %i-%02i-%02i %02i:%02i:%02i" % (tmsg_id, string.ljust(status, 8), string.ljust(username, 10), cpl.year, cpl.month, cpl.day, cpl.hour, cpl.minute, cpl.second))

                if result_header['status'] == 'error':
                    print("  Error was: " + result_content['evalue'])
            # for debugging:
            #print(task)
    
if __name__ == "__main__":
    main()
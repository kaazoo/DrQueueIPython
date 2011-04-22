# -*- coding: utf-8 -*-

import string
import DrQueue
from DrQueue import Job as DrQueueJob
from DrQueue import Client as DrQueueClient


def main():
    # initialize DrQueue client
    client = DrQueueClient()
    # fetch a list of all jobs
    jobs = client.query_all_jobs()
        
    # walk through tasks of every job
    for job in jobs:
        jmsg_id = job['msg_id']
        jheader = job['header']
        tasks = []
        
        print("\nTasks of job %s:" % jmsg_id)
        print("msg_id                                 status    owner       completed at")
        
        for task_id in jheader['after']:
            task = client.query_task(task_id)
            
            tmsg_id = task['msg_id']
            theader = task['header']
            username = theader['username']
        
            if task['completed'] == None:
                status = "pending"
            else:
                result_header = task['result_header']
                status = result_header['status']
                cpl = task['completed']
                result_content = eval(task['result_content'])
                result_buffers = eval(task['result_content'])
                buffers = task['buffers']
                pyerr = task['pyout']
    
            print("%s   %s  %s  %i-%02i-%02i %02i:%02i:%02i" % (tmsg_id, string.ljust(status, 8), string.ljust(username, 10), cpl.year, cpl.month, cpl.day, cpl.hour, cpl.minute, cpl.second))
        #print(result_content)
        #print(result_buffers)
        #print(buffers)
        #print(pyerr)
    
if __name__ == "__main__":
    main()
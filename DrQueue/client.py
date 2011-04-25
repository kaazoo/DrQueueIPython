# -*- coding: utf-8 -*-

import os
import time
from IPython.parallel import Client as IPClient
import DrQueue

class Client():
    """Class for client actions"""
    def __init__(self):
        # initialize IPython
        self.ip_client = IPClient()
        self.lbview = self.ip_client.load_balanced_view()


    """Wrapper for creating sub tasks and dummy task"""
    def run_job(self, job):
        # set session name which will be used as job name
        self.ip_client.session.session = job['name']

        task_frames = range(job['startframe'], job['endframe'] + 1, job['blocksize'])
        for x in task_frames:
            # prepare script input
            env_dict = {
            'DRQUEUE_OS' : DrQueue.get_osname(),
            'DRQUEUE_ETC' : os.getenv('DRQUEUE_ROOT') + "/etc",
            'DRQUEUE_FRAME' : x,
            'DRQUEUE_BLOCKSIZE' : job['blocksize'],
            'DRQUEUE_ENDFRAME' : job['endframe'],
            'SCENE' : job['scene'],
            'RENDER_TYPE' : "animation"
            }
    
            # run task on cluster
            render_script = os.getenv('DRQUEUE_ROOT') + "/etc/" + DrQueue.get_rendertemplate(job['renderer'])
            ar = self.lbview.apply(DrQueue.run_script_with_env, render_script, env_dict)
            # avoid race condition
            time.sleep(0.5)


    """Query a list of all jobs (IPython sessions)"""
    def query_all_jobs(self):
        jobs = []
        query_data = self.ip_client.db_query({"header.session" : {"$ne" : ""}}, keys=["header.session"])
        for entry in query_data:
            jobs.append(entry['header']['session'])
        jobs = set(jobs)
        jobs = list(jobs)
        jobs.sort()
        return jobs


    """Query a list of tasks objects of certain job"""
    def query_tasks_of_job(self, jobname):
        tasks = self.ip_client.db_query({"header.session" : jobname})
        return tasks


    """Query a single task"""
    def query_task(self, task_id):
        dict = {'msg_id': task_id }
        task = self.ip_client.db_query(dict)[0]
        return task


    """Stop job and all tasks which are not currently running"""
    def job_stop(self, jobname):
        tasks = self.query_tasks_of_job(jobname)

        # abort all queued tasks
        for task in tasks:
            self.ip_client.abort(task['msg_id'])

        return True


    """Stop job and all of it's tasks wether running or not"""
    def job_kill(self, jobname):
        tasks = self.query_tasks_of_job(jobname)

        # abort all queued tasks
        for task in tasks:
            self.lbview.abort(task['msg_id'])

        return True


    """Delete job and all of it's tasks"""
    def job_delete(self, jobname):
        tasks = self.query_tasks_of_job(jobname)

        # abort and delete all queued tasks
        for task in tasks:
            self.lbview.abort(task['msg_id'])
            self.ip_client.purge_results(task['msg_id'])

        return True


    def job_continue(self, jobname):
        return True


    """Return status string of job"""
    def job_status(self, jobname):
        job = self.query_task(job_id)

        if job['completed'] == None:
            status = "pending"
        else:
            result_header = job['result_header']
            status = result_header['status']
        return status



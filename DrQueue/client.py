# -*- coding: utf-8 -*-

import os
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
            job['tasks'].append(ar)

        # make dummy task depend on the others
        # we will track this one like a job
        self.lbview.set_flags(after=job['tasks'])
        job['dummy_task'] = self.lbview.apply(DrQueue.run_dummy)

    """Query a list of all 'job' tasks"""
    def query_all_jobs(self):
        dict = {'msg_id': { '$ne' : '' }}
        entries = self.ip_client.db_query(dict)
        jobs = []

        # fetch list of jobs
        for entry in entries:
            msg_id = entry['msg_id']
            header = entry['header']

            if header['after'] != []:
                jobs.append(entry)
        return jobs

    """Query a single task"""
    def query_task(self, task_id):
        dict = {'msg_id': task_id }
        task = self.ip_client.db_query(dict)[0]
        return task

    """Stop job and all tasks which are not currently running"""
    def job_stop(self, job_id):
        dict = {'msg_id': job_id }
        job = self.ip_client.db_query(dict)[0]
        header = job['header']

        # abort all queued tasks
        for task_id in header['after']:
            self.ip_client.abort(task_id)

        # abort job as well
        self.ip_client.abort(job_id)
        return True

    """Stop job and all of it's tasks wether running or not"""
    def job_kill(self, job_id):
        dict = {'msg_id': job_id }
        job = self.ip_client.db_query(dict)[0]
        header = job['header']

        # abort all queued tasks
        for task_id in header['after']:
            self.lbview.abort(task_id)

        # abort job as well
        self.lbview.abort(job_id)
        return True


    """Delete job and all of it's tasks"""
    def job_delete(self, job_id):
        dict = {'msg_id': job_id }
        job = self.ip_client.db_query(dict)[0]
        header = job['header']

        # abort and delete all queued tasks
        for task_id in header['after']:
            self.lbview.abort(task_id)
            self.ip_client.purge_results(task_id)

        # abort and delete job as well
        self.lbview.abort(job_id)
        self.ip_client.purge_results(job_id)
        return True

    def job_continue(self, job_id):
        return True

    """Return status string of job"""
    def job_status(self, job_id):
        job = self.query_task(job_id)

        if job['completed'] == None:
            status = "pending"
        else:
            result_header = job['result_header']
            status = result_header['status']
        return status



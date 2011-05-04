# -*- coding: utf-8 -*-

"""
DrQueue Client submodule
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os
import os.path
import time
from IPython.parallel import Client as IPClient
from IPython.parallel.util import unpack_apply_message
import DrQueue

class Client():
    """DrQueue client actions"""
    def __init__(self):
        # initialize IPython
        self.ip_client = IPClient()
        self.lbview = self.ip_client.load_balanced_view()


    def job_run(self, job):
        """Create and queue tasks from job object"""

        # check job name
        if job['name'] in self.query_job_list():
            raise ValueError("Job name %s is already used!" % job['name'])
            return False

        # set session name which will be used as job name
        self.ip_client.session.session = job['name']

        # check frame numbers
        if not (job['endframe'] >= job['blocksize'] >= job['startframe'] >= 1):
            raise ValueError("Invalid values for frame numbers!")
            return False

        task_frames = range(job['startframe'], job['endframe'] + 1, job['blocksize'])
        for x in task_frames:
            # prepare script input
            env_dict = {
            'DRQUEUE_OS' : DrQueue.get_osname(),
            'DRQUEUE_ETC' : os.path.join(os.getenv('DRQUEUE_ROOT'), "etc"),
            'DRQUEUE_FRAME' : x,
            'DRQUEUE_BLOCKSIZE' : job['blocksize'],
            'DRQUEUE_ENDFRAME' : job['endframe'],
            'DRQUEUE_SCENEFILE' : job['scenefile'],
            'DRQUEUE_LOGFILE' : os.path.join(os.getenv('DRQUEUE_ROOT'), "logs", job['name'] + "-" + str(x) + "_" + str(x + job['blocksize'] -1) + ".log")
            }

            # optional elements
            if 'renderdir' in job:
                env_dict['DRQUEUE_RENDERDIR'] = job['renderdir']
            if 'projectdir' in job:
                env_dict['DRQUEUE_PROJECTDIR'] = job['projectdir']
            if 'configdir' in job:
                env_dict['DRQUEUE_CONFIGDIR'] = job['configdir']
            if 'imagefile' in job:
                env_dict['DRQUEUE_IMAGEFILE'] = job['imagefile']
            if 'precommand' in job:
                env_dict['DRQUEUE_PRECOMMAND'] = job['precommand']
            if 'postcommand' in job:
                env_dict['DRQUEUE_POSTCOMMAND'] = job['postcommand']
            if 'viewcommand' in job:
                env_dict['DRQUEUE_VIEWCOMMAND'] = job['viewcommand']
            if 'worldfile' in job:
                env_dict['DRQUEUE_WORLDFILE'] = job['worldfile']
            if 'terrainfile' in job:
                env_dict['DRQUEUE_TERRAINFILE'] = job['terrainfile']
            if 'composition' in job:
                env_dict['DRQUEUE_COMPOSITION'] = job['composition']
            if 'camera' in job:
                env_dict['DRQUEUE_CAMERA'] = job['camera']
            if 'resx' in job:
                env_dict['DRQUEUE_RESX'] = job['resx']
            if 'resy' in job:
                env_dict['DRQUEUE_RESY'] = job['resy']
            if 'renderpass' in job:
                env_dict['DRQUEUE_RENDERPASS'] = job['renderpass']
            if 'rendertype' in job:
                env_dict['DRQUEUE_RENDERTYPE'] = job['rendertype']
            if 'fileextension' in job:
                env_dict['DRQUEUE_FILEEXTENSION'] = job['fileextension']
    
            # run task on cluster
            render_script = os.path.join(os.getenv('DRQUEUE_ROOT'), "etc", DrQueue.get_rendertemplate(job['renderer']))
            ar = self.lbview.apply(DrQueue.run_script_with_env, render_script, env_dict)
            # avoid race condition
            time.sleep(0.5)


    def task_wait(self, task_id):
        """Wait for task to finish"""
        ar = self.ip_client.get_result(task_id)
        ar.wait()
        return ar


    def query_job_list(self):
        """Query a list of all jobs (IPython sessions)"""
        jobs = []
        query_data = self.ip_client.db_query({"header.session" : {"$ne" : ""}}, keys=["header.session"])
        for entry in query_data:
            jobs.append(entry['header']['session'])
        jobs = set(jobs)
        jobs = list(jobs)
        jobs.sort()
        return jobs


    def query_jobname(self, task_id):
        """Query jobname from task id"""
        data = self.ip_client.db_query({"msg_id" : task_id})
        jobname = data[0]['header']['session']
        return jobname


    def query_task_list(self, jobname):
        """Query a list of tasks objects of certain job"""
        tasks = self.ip_client.db_query({"header.session" : jobname})
        return tasks


    def query_task(self, task_id):
        """Query a single task"""
        dict = {'msg_id': task_id }
        task = self.ip_client.db_query(dict)[0]
        return task


    def query_engine_list(self):
        """Query a list of all engines"""
        return self.ip_client.ids


    def job_stop(self, jobname):
        """Stop job and all tasks which are not currently running"""
        tasks = self.query_task_list(jobname)
        # abort all queued tasks
        for task in tasks:
            self.ip_client.abort(task['msg_id'])
        return True


    def job_kill(self, jobname):
        """Stop job and all of it's tasks wether running or not"""
        tasks = self.query_task_list(jobname)
        running_engines = []
        # abort all queued tasks
        for task in tasks:
            stats = self.ip_client.queue_status('all', True)
            # check if tasks is already running on an engine
            for key,status in stats.items():
                if ('tasks' in status) and (task['msg_id'] in status['tasks']):
                    print "found"
                    running_engines.append(key)
            self.ip_client.abort(task['msg_id'])
        # restart all engines which still run a task
        running_engines = set(running_engines)
        print list(running_engines)
        #for engine_id in running_engines:
        #    self.ip_client(engine_id)
        return True


    def job_delete(self, jobname):
        """Delete job and all of it's tasks"""
        tasks = self.query_task_list(jobname)
        # abort and delete all queued tasks
        for task in tasks:
            self.ip_client.abort(task['msg_id'])
            self.ip_client.purge_results(task['msg_id'])
        return True


    def task_continue(self, task_id):
        """Continue aborted or failed task"""
        task = self.query_task(task_id)
        # check if action is needed
        if (task['completed'] != None) and ((task['result_header']['status'] == "error") or (task['result_header']['status'] == "aborted")):
            print "requeuing %s" % task_id
            self.task_requeue(task_id)
        return True


    def task_requeue(self, task_id):
        """Requeue task"""
        # get the buffers from the Hub
        rec = self.ip_client.db_query(dict(msg_id=task_id), keys=['buffers'])[0]
        # reconstruct the arguments
        f,args,kwargs = unpack_apply_message(rec['buffers'])
        # resubmit to old session
        self.ip_client.session.session = self.query_jobname(task_id)
        self.lbview.apply_async(f,*args,**kwargs)
        # remove old entry
        self.ip_client.purge_results(task_id)
        return True


    def job_continue(self, jobname):
        """Continue stopped job and all of it's tasks"""
        tasks = self.query_task_list(jobname)
        # continue tasks
        for task in tasks:
            self.task_continue(task['msg_id'])
        return True


    def job_status(self, jobname):
        """Return status string of job"""
        job = self.query_task(job_id)
        if job['completed'] == None:
            status = "pending"
        else:
            result_header = job['result_header']
            status = result_header['status']
        return status


    def engine_stop(self, engine_id):
        """Stop a specific engine"""
        self.ip_client.shutdown(engine_id, False, False, True)
        return True


    def engine_restart(self, engine_id):
        """Restart a specific engine"""
        self.ip_client.shutdown(engine_id, True, False, True)
        return True



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
from job import Job as DrQueueJob
from computer_pool import ComputerPool as DrQueueComputerPool

class Client():
    """DrQueue client actions"""
    def __init__(self):
        # initialize IPython
        self.ip_client = IPClient()
        self.lbview = self.ip_client.load_balanced_view()

        # enable tracking
        self.lbview.track = True


    def job_run(self, job):
        """Create and queue tasks from job object"""

        # check job name
        if job['name'] in DrQueueJob.query_jobnames():
            raise ValueError("Job name %s is already used!" % job['name'])
            return False

        # only work on available engines
        if self.query_ready_engines_of_pool(job['pool']) == False:
            return False

        # save job in database
        job_id = DrQueueJob.store_db(job)

        # job_id from db is be used as session name
        self.ip_client.session.session = str(job_id)

        # set owner of job
        self.ip_client.session.username = job['owner']

        # set number of retries for each task
        self.lbview.retries = job['retries']

        # check frame numbers
        if not (job['startframe'] >= 1):
            raise ValueError("Invalid value for startframe. Has to be equal or greater than 1.")
            return False
        if not (job['endframe'] >= 1):
            raise ValueError("Invalid value for endframe. Has to be equal or greater than 1.")
            return False
        if not (job['endframe'] >= job['startframe']):
            raise ValueError("Invalid value for endframe. Has be to equal or greater than startframe.")
            return False
        if job['endframe'] > job['startframe']:
            if not (job['endframe'] - job['startframe'] >= job['blocksize']):
                raise ValueError("Invalid value for blocksize. Has to be equal or lower than endframe-startframe.")
                return False
        if job['endframe'] == job['startframe']:
            if job['blocksize'] != 1:
                raise ValueError("Invalid value for blocksize. Has to be equal 1 if endframe equals startframe.")
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
            if 'renderer' in job:
                env_dict['DRQUEUE_RENDERER'] = job['renderer']
            if 'fileformat' in job:
                env_dict['DRQUEUE_FILEFORMAT'] = job['fileformat']
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
            # wait for pyzmq send to complete communication (avoid race condition)
            ar.wait_for_send()


    def identify_computer(self, engine_id):
        """Gather information about computer"""
        # run command only on specific computer
        dview = self.ip_client[engine_id]
        dview.block = True
        dview.execute("import DrQueue\nfrom DrQueue import Computer as DrQueueComputer\nc = DrQueueComputer("+str(engine_id)+")")
        return dview['c']


    def task_wait(self, task_id):
        """Wait for task to finish"""
        ar = self.ip_client.get_result(task_id)
        ar.wait_for_send()
        ar.wait()
        return ar


    def query_job_list(self):
        """Query a list of all jobs"""
        return DrQueueJob.query_job_list()


    def query_jobname(self, task_id):
        """Query jobname from task id"""
        data = self.ip_client.db_query({"msg_id" : task_id})
        job_id = data[0]['header']['session']
        job = DrQueueJob.query_db(job_id)
        return job.name


    def query_job(self, job_id):
        """Query job from id"""
        return DrQueueJob.query_db(job_id)


    def query_job_by_name(self, job_name):
        """Query job from name"""
        return DrQueueJob.query_job_by_name(job_name)


    def query_task_list(self, job_id):
        """Query a list of tasks objects of certain job"""
        tasks = []
        query_data = self.ip_client.db_query({"header" : {"$ne" : ""}})
        for entry in query_data:
            if (entry['header'] != None) and (str(entry['header']['session']) == str(job_id)):
                tasks.append(entry)
        return tasks


    def query_task(self, task_id):
        """Query a single task"""
        task = self.ip_client.db_query({'msg_id' : task_id })[0]
        return task


    def query_engine_list(self):
        """Query a list of all engines"""
        return self.ip_client.ids


    def query_ready_engines_of_pool(self, pool_name):
        """Query list of pool members and return only available engines"""
        ready_computers = []
        # update LoadBalancedView if pool is set
        if pool_name != None:
            computers = list(DrQueueComputerPool.query_pool_members(pool_name))
            for comp in computers:
                if comp in self.query_engine_list():
                    ready_computers.append(comp)
            if ready_computers == []:
                raise ValueError("No computer of pool %s is available!" % pool_name)
                return False
            self.lbview = self.ip_client.load_balanced_view(ready_computers)
        # load balance on all existing computers
        else:
            self.lbview = self.ip_client.load_balanced_view()
        return True

    def job_stop(self, job_id):
        """Stop job and all tasks which are not currently running"""
        tasks = self.query_task_list(job_id)
        # abort all queued tasks
        for task in tasks:
            self.ip_client.abort(task['msg_id'])
        return True


    def job_kill(self, job_id):
        """Stop job and all of it's tasks wether running or not"""
        tasks = self.query_task_list(job_id)
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


    def job_delete(self, job_id):
        """Delete job and all of it's tasks"""
        tasks = self.query_task_list(job_id)
        # abort and delete all queued tasks
        for task in tasks:
            self.ip_client.abort(task['msg_id'])
            self.ip_client.purge_results(task['msg_id'])
        # delete job itself
        DrQueueJob.delete_from_db(job_id)
        return True


    def task_continue(self, task_id):
        """Continue aborted or failed task"""
        task = self.query_task(task_id)
        # check if action is needed
        if (task['completed'] != None) and ((task['result_header']['status'] == "error") or (task['result_header']['status'] == "aborted")):
            self.task_requeue(task_id)
        return True


    def task_requeue(self, task_id):
        """Requeue task"""
        self.ip_client.resubmit(task_id)
        print "requeuing %s" % task_id
        return True


    def job_continue(self, job_id):
        """Continue stopped job and all of it's tasks"""
        tasks = self.query_task_list(job_id)
        # continue tasks
        for task in tasks:
            self.task_continue(task['msg_id'])
        return True


    def job_rerun(self, job_id):
        """Run all tasks of job another time"""
        tasks = self.query_task_list(job_id)
        # rerun tasks
        for task in tasks:
            self.task_requeue(task['msg_id'])
        return True


    def job_status(self, job_id):
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



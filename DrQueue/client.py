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
import pickle
import datetime
from IPython.parallel import Client as IPClient
from IPython.parallel.util import unpack_apply_message
from IPython.parallel import dependent
import DrQueue
from .job import Job as DrQueueJob
from .computer import Computer as DrQueueComputer
from .computer_pool import ComputerPool as DrQueueComputerPool

class Client():
    """DrQueue client actions"""
    def __init__(self):
        # initialize IPython
        try:
            self.ip_client = IPClient()
        except Exception:
            raise Exception("Could not connect to IPython controller.")
        self.lbview = self.ip_client.load_balanced_view()

        # enable tracking
        self.lbview.track = True


    def job_run(self, job):
        """Create and queue tasks from job object"""

        # check job name
        if job['name'] in DrQueueJob.query_jobnames():
            raise ValueError("Job name %s is already used!" % job['name'])
            return False

        # save job in database
        job_id = DrQueueJob.store_db(job)

        # job_id from db is be used as session name
        self.ip_client.session.session = str(job_id)

        # set owner of job
        self.ip_client.session.username = job['owner']

        # set number of retries for each task
        self.lbview.retries = job['retries']

        # depend on another job (it's tasks)
        if ('depend' in job['limits']) and (job['limits']['depend'] != None):
            depend_job = self.query_job_by_name(job['limits']['depend'])
            depend_tasks = self.query_task_list(depend_job['_id'])
            task_ids = []
            for task in depend_tasks:
                task_ids.append(task['msg_id'])
            self.lbview.after = task_ids

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

        task_frames = list(range(job['startframe'], job['endframe'] + 1, job['blocksize']))
        ar = None
        for x in task_frames:
            # prepare script input
            env_dict = {
            'DRQUEUE_FRAME' : x,
            'DRQUEUE_BLOCKSIZE' : job['blocksize'],
            'DRQUEUE_ENDFRAME' : job['endframe'],
            'DRQUEUE_SCENEFILE' : job['scenefile'],
            'DRQUEUE_LOGFILE' : job['name'] + "-" + str(x) + "_" + str(x + job['blocksize'] -1) + ".log"
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
            if 'stepframe' in job:
                env_dict['DRQUEUE_STEPFRAME'] = job['stepframe']
            if 'custom_bucket' in job:
                env_dict['DRQUEUE_CUSTOM_BUCKET'] = job['custom_bucket']
            if 'bucketsize' in job:
                env_dict['DRQUEUE_BUCKETSIZE'] = job['bucketsize']
            if 'custom_lod' in job:
                env_dict['DRQUEUE_CUSTOM_LOD'] = job['custom_lod']
            if 'lod' in job:
                env_dict['DRQUEUE_LOD'] = job['lod']
            if 'custom_varyaa' in job:
                env_dict['DRQUEUE_CUSTOM_VARYAA'] = job['custom_varyaa']
            if 'varyaa' in job:
                env_dict['DRQUEUE_VARYAA'] = job['varyaa']
            if 'raytrace' in job:
                env_dict['DRQUEUE_RAYTRACE'] = job['raytrace']
            if 'antialias' in job:
                env_dict['DRQUEUE_ANTIALIAS'] = job['antialias']
            if 'custom_bdepth' in job:
                env_dict['DRQUEUE_CUSTOM_BDEPTH'] = job['custom_bdepth']
            if 'bdepth' in job:
                env_dict['DRQUEUE_BDEPTH'] = job['bdepth']
            if 'custom_zdepth' in job:
                env_dict['DRQUEUE_CUSTOM_ZDEPTH'] = job['custom_zdepth']
            if 'zdepth' in job:
                env_dict['DRQUEUE_ZDEPTH'] = job['zdepth']
            if 'custom_cracks' in job:
                env_dict['DRQUEUE_CUSTOM_CRACKS'] = job['custom_cracks']
            if 'cracks' in job:
                env_dict['DRQUEUE_CRACKS'] = job['cracks']
            if 'custom_quality' in job:
                env_dict['DRQUEUE_CUSTOM_QUALITY'] = job['custom_quality']
            if 'quality' in job:
                env_dict['DRQUEUE_QUALITY'] = job['quality']
            if 'custom_qfiner' in job:
                env_dict['DRQUEUE_CUSTOM_QFINER'] = job['custom_qfiner']
            if 'qfiner' in job:
                env_dict['DRQUEUE_QFINER'] = job['qfiner']
            if 'custom_smultiplier' in job:
                env_dict['DRQUEUE_CUSTOM_SMULTIPLIER'] = job['custom_smultiplier']
            if 'smultiplier' in job:
                env_dict['DRQUEUE_SMULTIPLIER'] = job['smultiplier']
            if 'custom_mpcache' in job:
                env_dict['DRQUEUE_CUSTOM_MPCACHE'] = job['custom_mpcache']
            if 'mpcache' in job:
                env_dict['DRQUEUE_MPCACHE'] = job['mpcache']
            if 'custom_smpolygon' in job:
                env_dict['DRQUEUE_CUSTOM_SMPOLYGON'] = job['custom_smpolygon']
            if 'smpolygon' in job:
                env_dict['DRQUEUE_SMPOLYGON'] = job['smpolygon']
            if 'custom_wh' in job:
                env_dict['DRQUEUE_CUSTOM_WH'] = job['custom_wh']
            if 'custom_type' in job:
                env_dict['DRQUEUE_CUSTOM_TYPE'] = job['custom_type']
            if 'ctype' in job:
                env_dict['DRQUEUE_CTYPE'] = job['ctype']
            if 'skipframes' in job:
                env_dict['DRQUEUE_SKIPFRAMES'] = job['skipframes']

            # set dependencies
            dep_dict = {}
            if ('os' in job['limits']) and (job['limits']['os'] != None):
                dep_dict['os_name'] = job['limits']['os']
            if ('minram' in job['limits']) and (job['limits']['minram'] > 0):
                dep_dict['minram'] = job['limits']['minram']
            if ('mincores' in job['limits']) and (job['limits']['mincores'] > 0):
                dep_dict['mincores'] = job['limits']['mincores']
            if ('pool_name' in job['limits']) and (job['limits']['pool_name'] != None):
                dep_dict['pool_name'] = job['limits']['pool_name']
            run_script_with_env_and_deps = dependent(DrQueue.run_script_with_env, DrQueue.check_deps, dep_dict)

            # run task on cluster
            render_script = DrQueue.get_rendertemplate(job['renderer'])
            ar = self.lbview.apply(run_script_with_env_and_deps, render_script, env_dict)
            # wait for pyzmq send to complete communication (avoid race condition)
            ar.wait_for_send()

        # append email task behind last task if requested
        if ('send_email' in job) and (job['send_email'] == True):
            self.lbview.after = ar
            # run email task
            mail_ar = self.lbview.apply(DrQueue.send_email, job['name'], job['email_recipients'])
            # wait for pyzmq send to complete communication (avoid race condition)
            mail_ar.wait_for_send()
        return True


    def identify_computer(self, engine_id, cache_time):
        """Gather information about computer"""
        # look if engine info is already stored
        engine = DrQueueComputer.query_db(engine_id)
        now = int(time.time())
        # check existence and age of info
        if (engine != None) and (now <= engine['date'] + cache_time):
            print("DEBUG: Engine %i was found in DB" % engine_id)
        # store new info
        else:
            print("DEBUG: Engine %i was not found in DB" % engine_id)
            # run command only on specific computer
            dview = self.ip_client[engine_id]
            dview.block = True
            dview.execute("import DrQueue\nfrom DrQueue import Computer as DrQueueComputer\nengine = DrQueueComputer(" + str(engine_id) + ")")
            engine = dview['engine']
            engine['date'] = int(time.time())
            DrQueueComputer.store_db(engine)
        return engine


    def task_wait(self, task_id):
        """Wait for task to finish"""
        ar = self.ip_client.get_result(task_id)
        ar.wait_for_send()
        ar.wait()
        return ar


    def query_job_list(self):
        """Query a list of all jobs"""
        return DrQueueJob.query_job_list()


    def query_running_job_list(self):
        """Query a list of all running jobs"""
        jobs = DrQueueJob.query_job_list()
        running_jobs = []
        for job in jobs:
            if self.query_job_tasks_left(job['_id']) > 0:
                running_jobs.append(job)
        return running_jobs


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


    def query_job_tasks_left(self, job_id):
        """Query left frames of job"""
        left = 0
        tasks = self.query_task_list(job_id)
        for task in tasks:
            if task['completed'] == None:
                left += 1
        return left


    def query_job_finish_time(self, job_id):
        """Query oldest finish time of all tasks."""
        job = self.query_job(job_id)
        # use requeue time as starting point if available
        if ('requeue_time' in job ) and (job['requeue_time'] != False):
            finish_time = job['requeue_time']
        else:
            finish_time = job['submit_time']
        tasks = self.query_task_list(job_id)
        for task in tasks:
            # look if older finish time exists
            if (task['completed'] != None) and (task['completed'] > finish_time):
                finish_time = task['completed']
        return finish_time


    def get_frame_nr(self, task):
        """Extract value of DRQUEUE_FRAME."""
        return int(pickle.loads(task['buffers'][3])['DRQUEUE_FRAME'])


    def query_task_list(self, job_id):
        """Query a list of tasks objects of certain job"""
        task_list =  self.ip_client.db_query({'header.session' : str(job_id)})
        sorted_task_list = sorted(task_list, key=self.get_frame_nr)
        return sorted_task_list


    def query_task(self, task_id):
        """Query a single task"""
        task = self.ip_client.db_query({'msg_id' : task_id })[0]
        return task


    def query_engine_list(self):
        """Query a list of all engines"""
        return self.ip_client.ids


    def query_engines_of_pool(self, pool_name):
        """Return available engines of certain pool."""
        pool_computers = self.ip_client.ids
        if pool_name != None:
            computers = DrQueueComputerPool.query_pool_members(pool_name)
            if computers == None:
                raise ValueError("Pool \"%s\" is not existing!" % pool_name)
                return False
            for comp in pool_computers:
                if not comp in computers:
                    pool_computers.remove(comp)
            if pool_computers == []:
                raise ValueError("No computer of pool %s is available!" % pool_name)
                return False
            print("DEBUG: matching pool: " + pool_name)
            print(pool_computers)
        return pool_computers


    def query_engines_of_os(self, os_name):
        """Return only engines running certain OS."""
        # run job only on matching os
        matching_os = self.ip_client.ids
        if os_name != None:
            for engine_id in self.ip_client.ids:
                engine = self.identify_computer(engine_id, 1000)
                # os string has to contain os_name
                if not os_name in engine['os']:
                    matching_os.remove(engine_id)
            print("DEBUG: matching os: " + os_name)
            print(matching_os)
        return matching_os


    def query_engines_with_minram(self, minram):
        """Return only engines with at least minram GB RAM."""
        # run job only on matching minram
        matching_minram = self.ip_client.ids
        if minram > 0:
            for engine_id in self.ip_client.ids:
                engine = self.identify_computer(engine_id, 1000)
                if engine['memory'] < minram:
                    matching_minram.remove(engine_id)
            print("DEBUG: matching minram: " + str(minram))
            print(matching_minram)
        return matching_minram


    def query_engines_with_mincores(self, mincores):
        """Return only engines with at least mincores CPU cores."""
        # run job only on matching mincores
        matching_mincores = self.ip_client.ids
        if mincores > 0:
            for engine_id in self.ip_client.ids:
                engine = self.identify_computer(engine_id, 1000)
                if engine['ncorescpu'] * engine['ncpus'] < mincores:
                    matching_mincores.remove(engine_id)
            print("DEBUG: matching mincores: " + str(mincores))
            print(matching_mincores)
        return matching_mincores


    def match_all_limits(self, os_list, minram_list, mincores_list, pool_list):
        """Match all limits for job."""
        tmp_list = []
        # build list with all list members
        tmp_list.extend(os_list)
        tmp_list.extend(minram_list)
        tmp_list.extend(mincores_list)
        tmp_list.extend(pool_list)
        # make entries unique
        tmp_list = set(tmp_list)
        tmp_list = list(tmp_list)
        matching_limits = []
        for entry in tmp_list:
            # look if entry is in all lists
            if (entry in os_list) and (entry in minram_list) and (entry in mincores_list) and (entry in pool_list):
                matching_limits.append(entry)
            else:
                print("DEBUG: %i isn't matching limits" % entry)
        print("DEBUG: matching limits:")
        print(matching_limits)
        if len(matching_limits) == 0:
            message = "No engine meets the requirements."
            print(message)
            raise Exception(message)
        elif len(matching_limits) > 0:
            # only run on matching engines
            self.lbview = self.ip_client.load_balanced_view(matching_limits)
        else:
            self.lbview = self.ip_client.load_balanced_view()


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
            for key,status in list(stats.items()):
                if ('tasks' in status) and (task['msg_id'] in status['tasks']):
                    running_engines.append(key)
            self.ip_client.abort(task['msg_id'])
        # restart all engines which still run a task
        running_engines = set(running_engines)
        return True


    def job_delete(self, job_id):
        """Delete job and all of it's tasks"""
        tasks = self.query_task_list(job_id)
        engines = self.query_engine_list()
        # abort and delete all queued tasks
        for task in tasks:
            if len(engines) > 0:
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
        print("requeuing %s" % task_id)
        return True


    def job_continue(self, job_id):
        """Continue stopped job and all of it's tasks"""
        job = self.query_job(job_id)
        tasks = self.query_task_list(job_id)
        # continue tasks
        for task in tasks:
            self.task_continue(task['msg_id'])
        return True


    def job_rerun(self, job_id):
        """Run all tasks of job another time"""
        job = self.query_job(job_id)
        tasks = self.query_task_list(job_id)
        # rerun tasks
        for task in tasks:
            self.task_requeue(task['msg_id'])
        # set resubmit time
        job['requeue_time'] = datetime.datetime.now()
        DrQueueJob.update_db(job)
        return True


    def job_status(self, job_id):
        """Return status string of job"""
        tasks = self.query_task_list(job_id)
        status = None
        status_pending = 0
        status_ok = 0
        status_aborted = 0
        status_resubmitted = 0
        status_error = 0
        status_unknown = 0
        for task in tasks:
            # look for pending tasks
            if task['completed'] == None:
                status_pending += 1
            else:
                if 'result_header' in list(task.keys()):
                    result_header = task['result_header']
                    # look for done tasks
                    if ('status' in list(result_header.keys())) and (result_header['status'] == "ok"):
                        status_ok += 1
                    # look for aborted tasks
                    elif ('status' in list(result_header.keys())) and (result_header['status'] == "aborted"):
                        status_aborted += 1
                    # look for done tasks
                    elif ('status' in list(result_header.keys())) and (result_header['status'] == "resubmitted"):
                        status_resubmitted += 1
                    # look for tasks with error
                    elif ('status' in list(result_header.keys())) and (result_header['status'] == "error"):
                        status_error += 1
                    else:
                        status_unknown += 1
        # if at least 1 task is ok, job status is ok
        if status_ok > 0:
            status = "ok"
        # if at least 1 task is pending, job status is pending
        if status_pending > 0:
            status = "pending"
        # if at least 1 task is aborted, job status is aborted
        if status_aborted > 0:
            status = "aborted"
        # if at least 1 task has an error, job status is error
        if status_error > 0:
            status = "error"
        return status


    def job_estimated_finish_time(self, job_id):
        """Calculate estimated finish time of job."""
        tasks = self.query_task_list(job_id)
        spent_times = []
        # get spent time for each finished task
        for task in tasks:
            if task['completed'] != None:
                if 'result_header' in list(task.keys()):
                    result_header = task['result_header']
                    if ('status' in list(result_header.keys())) and (result_header['status'] == "ok"):
                        timediff = task['completed'] - task['started']
                        spent_times.append(timediff)
        if len(spent_times) > 0:
            # calculate sum of spent time
            sum_times = datetime.timedelta(0)
            for spent in spent_times:
                sum_times += spent
            # calcutate mean time for a single task
            meantime = sum_times / len(spent_times)
            # calculate estimated time left
            tasks_left = len(tasks) - len(spent_times)
            time_left = tasks_left * meantime
            # query job object
            job = self.query_job(job_id)
            # look if all tasks are already done
            if self.query_job_tasks_left(job_id) == 0:
                finish_time = self.query_job_finish_time(job_id)
            else:
                # calculate estimated finish time, use requeue time if available
                if ('requeue_time' in job ) and (job['requeue_time'] != False):
                    finish_time = job['requeue_time'] + time_left
                else:
                    finish_time = job['submit_time'] + time_left
        else:
            meantime = "unknown"
            time_left = "unknown"
            finish_time = "unknown"
        return meantime, time_left, finish_time


    def engine_stop(self, engine_id):
        """Stop a specific engine"""
        # delete computer information in db
        DrQueueComputer.delete_from_db(engine_id)
        # shutdown computer
        self.ip_client.shutdown(engine_id)
        return True


    def engine_restart(self, engine_id):
        """Restart a specific engine"""
        self.ip_client.shutdown(engine_id, True, False, True)
        return True



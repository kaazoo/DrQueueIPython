# -*- coding: utf-8 -*-

"""
DrQueue Client submodule
Copyright (C) 2011,2012 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os
import os.path
import glob
import time
import pickle
import datetime
from IPython.parallel import Client as IPClient
from IPython.parallel.util import unpack_apply_message
from IPython.parallel import dependent
import DrQueue
from .job import Job as DrQueueJob
from .computer import Computer as DrQueueComputer


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

        # list of all available query keys
        self.all_task_query_keys = ['msg_id', 'header', 'content', 'buffers', 'submitted', 'client_uuid', 'engine_uuid', 'started', 'completed', 'resubmitted', 'result_header', 'result_content', 'result_buffers', 'queue', 'pyin', 'pyout', 'pyerr', 'stdout', 'stderr']


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
            'DRQUEUE_SCENEFILE' : job['scenefile']
            }

            # log filename
            if job['created_with'] == "DrQueueOnRails":
                # take job directory name
                env_dict['DRQUEUE_LOGFILE'] = job['scenefile'].split("/")[-2] + "-" + str(x) + "_" + str(x + job['blocksize'] -1) + ".log"
            else:
                # take job name
                env_dict['DRQUEUE_LOGFILE'] = job['name'] + "-" + str(x) + "_" + str(x + job['blocksize'] -1) + ".log"

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
            if 'custom_command' in job:
                env_dict['DRQUEUE_CUSTOM_COMMAND'] = job['custom_command']

            # set dependencies
            dep_dict = {}
            dep_dict['job_id'] = job_id
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


    def identify_computer(self, engine_id, cache_time, timeout=15):
        """Gather information about computer"""
        # look if engine info is already stored
        engine = DrQueueComputer.query_db_by_engine_id(engine_id)
        now = int(time.time())
        # check existence and age of info
        if (engine != None) and (now <= engine['created_at'] + cache_time):
            print("DEBUG: Engine %i was found in DB and info is up-to-date." % engine_id)
            return engine
        # store new info
        else:
            if engine != None:
                print("DEBUG: Engine %i was found in DB, but info needs to be updated." % engine_id)
            else:
                print("DEBUG: Engine %i was not found in DB." % engine_id)
            # run command only on specific computer
            try:
                dview = self.ip_client[engine_id]
            except IndexError:
                print("DEBUG: Engine with id %i unknown." % engine_id)
                # delete old entry from database
                DrQueueComputer.delete_from_db_by_engine_id(engine_id)
                print("DEBUG: Engine with id %i deleted from database." % engine_id)
                new_engine = None
            else:
                # run command in async mode
                dview.block = False
                command = "import DrQueue\nfrom DrQueue import Computer as DrQueueComputer\nengine = DrQueueComputer()"
                ar = dview.execute(command)
                try:
                    # try to get results & wait until timeout
                    ar.get(timeout)
                except Exception:
                    if engine != None:
                        print("DEBUG: Update request for engine %i timed out. Using old information from DB." % engine_id)
                        new_engine = engine
                    else:
                        print("DEBUG: Information request for engine %i timed out." % engine_id)
                        new_engine = None
                else:
                    # get computer dict from engine namespace
                    new_engine = dview['engine']
                    # set to known engine_id
                    new_engine['engine_id'] = engine_id
                    # set creation time
                    new_engine['created_at'] = int(time.time())
                    # store entry in database
                    DrQueueComputer.store_db(new_engine)
            return new_engine


    def computer_set_pools(self, computer, pool_list):
        """add computer to list of pools"""
        # convert to string
        pool_str = ','.join(pool_list)
        # update environment variable on engine
        dview = self.ip_client[computer['engine_id']]
        dview.block = True
        command = "import os\nos.environ[\"DRQUEUE_POOL\"] = \"" + pool_str + "\""
        dview.execute(command)
        # update database entry
        computer['pools'] = pool_list
        DrQueueComputer.store_db(computer)
        print("DEBUG: Engine " + str(computer['engine_id']) + " added to pools " + pool_str + ".")
        return computer


    def computer_get_pools(self, computer):
        """Return all pool names where computer is member."""
        return computer['pools']


    def task_wait(self, task_id):
        """Wait for task to finish"""
        ar = self.ip_client.get_result(task_id)
        ar.wait_for_send()
        ar.wait()
        return ar


    def query_job_list(self):
        """Query a list of all jobs"""
        return DrQueueJob.query_job_list()


    def query_job_by_id(self, job_id):
        """Query job by given id"""
        return DrQueueJob.query_db(job_id)


    def query_job_by_name(self, job_name):
        """Query job by given name"""
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
        job = self.query_job_by_id(job_id)
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
        if ('buffers' in task) and task['buffers'] != []:
            frame_nr = int(pickle.loads(task['buffers'][3])['DRQUEUE_FRAME'])
        else:
            frame_nr = 1
        return frame_nr


    def query_task_list(self, job_id):
        """Query a list of tasks objects of certain job. Sort by frame number."""
        task_list =  self.ip_client.db_query({'header.session' : str(job_id)}, keys=self.all_task_query_keys)
        sorted_task_list = sorted(task_list, key=self.get_frame_nr)
        return sorted_task_list


    def query_interrupted_task_list(self, job_id):
        """Query a list of interrupted tasks of certain job. Sort by frame number."""
        job = self.query_job_by_id(job_id)
        task_list =  self.ip_client.db_query({'header.session' : str(job_id)}, keys=self.all_task_query_keys)
        interrupted_task_list = []

        for task in task_list:
            frame_nr = self.get_frame_nr(task)
            print("frame_nr: " + str(frame_nr))
            # log filename
            if job['renderer'] == "blender":
                filesearch = job['scenefile'] + str("%04d" % frame_nr) + ".???"
                found = glob.glob(filesearch)
                # file was found
                if len(found) > 0:
                    outputfile = found[0]
                    print("outputfile: "+ str(outputfile))
                    filesize = os.path.getsize(outputfile)
                    print(filesize)
                    # file exists, but is empty
                    if filesize == 0:
                        interrupted_task_list.append(task)
                # file was not found
                else:
                    outputfile = None
                    print("outputfile: "+ str(outputfile))
                    if (task['completed'] == None) and (task['started'] == None):
                        interrupted_task_list.append(task)
            else:
                raise ValueError("Only Blender renderer supported so far.")

        return interrupted_task_list


    def query_task(self, task_id):
        """Query a single task."""
        task = self.ip_client.db_query({'msg_id' : task_id }, keys=self.all_task_query_keys)[0]
        return task


    def query_computer_list(self):
        """Query a list of all computers."""
        return self.ip_client.ids


    def job_stop(self, job_id):
        """Stop job and all tasks which are not currently running"""

        # disable job
        self.job_disable(job_id)

        tasks = self.query_task_list(job_id)
        tasks_to_stop = []
        for task in tasks:
            print("Task " + task["msg_id"] + ": ")
            if ("result_header" in task) and (task["result_header"] != None) and (task["result_header"]["status"] == "ok"):
                print("  finished at " + str(task["completed"]))
            else:
                # get task stats of all computers
                stats = self.ip_client.queue_status('all', True)
                # check if tasks is already running on an engine
                found_on_engine = False
                for key,status in list(stats.items()):
                    if ('tasks' in status) and (task['msg_id'] in status['tasks']):
                        # skip tasks which are already running on an engine
                        print("  not finished yet but already queued to engine. will leave it there.")
                        found_on_engine = True
                        break

                # if a task isn't already queueed/running on an engine, it should be safe to abort it
                if found_on_engine == False:
                    print("  not finished yet. will abort.")
                    tasks_to_stop.append(task['msg_id'])

        if len(tasks_to_stop) > 0:
            try:
                self.ip_client.abort(tasks_to_stop)
            except Exception as e:
                print("ERROR: " + str(e))

        return True


    def job_kill(self, job_id):
        """Stop job and all of it's tasks wether running or not"""

        # disable job
        self.job_disable(job_id)

        tasks = self.query_task_list(job_id)
        running_engines = []
        tasks_to_stop = []
        # abort all queued tasks
        for task in tasks:
            stats = self.ip_client.queue_status('all', True)
            # check if tasks is already running on an engine
            for key,status in list(stats.items()):
                if ('tasks' in status) and (task['msg_id'] in status['tasks']):
                    running_engines.append(key)
            tasks_to_stop.append(task['msg_id'])
        # stop all matching tasks at once
        try:
            self.ip_client.abort(tasks_to_stop)
        except Exception as e:
            print("ERROR: " + str(e))

        # stop all engines which still run a task
        # the slave wrapper will restart the engine
        running_engines = set(running_engines)
        for engine_id in running_engines:
            self.engine_stop(engine_id)
        return True


    def job_disable(self, job_id):
        """Disable job in database."""
        job = self.query_job_by_id(job_id)
        job['enabled'] = False
        DrQueueJob.update_db(job)
        return True


    def job_enable(self, job_id):
        """Disable job in database."""
        job = self.query_job_by_id(job_id)
        job['enabled'] = True
        DrQueueJob.update_db(job)
        return True


    def job_delete(self, job_id):
        """Delete job and all of it's tasks"""
        tasks = self.query_task_list(job_id)
        engines = self.query_computer_list()
        # abort and delete all queued tasks
        for task in tasks:
            if len(engines) > 0:
                self.ip_client.abort(task['msg_id'])
            self.ip_client.purge_results(task['msg_id'])
        # delete job itself
        DrQueueJob.delete_from_db(job_id)
        return True


    def job_continue(self, job_id):
        """Continue stopped job and all of it's tasks"""
        job = self.query_job_by_id(job_id)

        # enable job
        self.job_enable(job_id)

        tasks = self.query_task_list(job_id)
        tasks_to_resubmit = []
        for task in tasks:
            print("Task " + task["msg_id"] + ": ")
            if ("result_header" in task) and (task["result_header"] != None) and (task["result_header"]["status"] == "ok"):
                print("  finished at " + str(task["completed"]))
            else:
                print("  not finished yet. will resubmit.")
                tasks_to_resubmit.append(task["msg_id"])

        if len(tasks_to_resubmit) > 0:

            # resubmit all matching msg_ids at once
            try:
                async_results = self.ip_client.resubmit(tasks_to_resubmit)
            except Exception as e:
                print("ERROR: " + str(e))

            # IPython seems to give out new msg_ids instead of re-using the old ones
            for msg_id in async_results.msg_ids:
                print("got new msg_id: " + msg_id)

            # delete old tasks which now have a resubmitted clone
            try:
                self.ip_client.purge_results(tasks_to_resubmit)
            except Exception as e:
                print("ERROR: " + str(e))

        return True


    def job_rerun(self, job_id):
        """Run all tasks of job another time"""
        job = self.query_job_by_id(job_id)

        # enable job
        job['enabled'] = True
        # set resubmit time
        job['requeue_time'] = datetime.datetime.now()
        DrQueueJob.update_db(job)

        tasks = self.query_task_list(job_id)
        tasks_to_resubmit = []
        # get all msg_ids of job
        for task in tasks:
            tasks_to_resubmit.append(task["msg_id"])

        # resubmit all msg_ids at once
        try:
            async_results = self.ip_client.resubmit(tasks_to_resubmit)
        except Exception as e:
            print("ERROR: " + str(e))

        # IPython seems to give out new msg_ids instead of re-using the old ones
        for msg_id in async_results.msg_ids:
            print("got new msg_id: " + msg_id)

        # delete old tasks which now have a resubmitted clone
        try:
            self.ip_client.purge_results(tasks_to_resubmit)
        except Exception as e:
            print("ERROR: " + str(e))

        # kickstart all computers
        running_engines = []
        for task in tasks:
            stats = self.ip_client.queue_status('all', True)
            # check if tasks is already running on an engine
            for key,status in list(stats.items()):
                if ('tasks' in status) and (task['msg_id'] in status['tasks']):
                    running_engines.append(key)
        # stop all engines which still run a task
        # the slave wrapper will restart the engine
        running_engines = set(running_engines)
        for engine_id in running_engines:
            self.engine_stop(engine_id)

        return True


    def task_rerun(self, task_id):
        """Run task another time"""
        task = self.query_task(task_id)

        #print(task)

        # enable job
        #job['enabled'] = True
        # set resubmit time
        #job['requeue_time'] = datetime.datetime.now()
        #DrQueueJob.update_db(job)

        # resubmit msg_id of task
        try:
            async_results = self.ip_client.resubmit(task["msg_id"])
        except Exception as e:
            print("ERROR: " + str(e))

        # IPython seems to give out new msg_ids instead of re-using the old ones
        for msg_id in async_results.msg_ids:
            print("got new msg_id: " + msg_id)

        # delete old tasks which now have a resubmitted clone
        try:
            self.ip_client.purge_results(task["msg_id"])
        except Exception as e:
            print("ERROR: " + str(e))

        # kickstart all computers
        running_engines = []
        stats = self.ip_client.queue_status('all', True)
        # check if tasks is already running on an engine
        for key,status in list(stats.items()):
            if ('tasks' in status) and (task['msg_id'] in status['tasks']):
                running_engines.append(key)
        # stop all engines which still run a task
        # the slave wrapper will restart the engine
        running_engines = set(running_engines)
        for engine_id in running_engines:
            self.engine_stop(engine_id)

        return True


    def job_rerun_interrupted_tasks(self, job_id):
        """Run interrupted tasks of job another time"""
        job = self.query_job_by_id(job_id)

        # enable job
        job['enabled'] = True
        # set resubmit time
        job['requeue_time'] = datetime.datetime.now()
        DrQueueJob.update_db(job)

        tasks = self.query_interrupted_task_list(job_id)

        if len(tasks) == 0:
            return True

        tasks_to_resubmit = []
        # get all msg_ids of job
        for task in tasks:
            tasks_to_resubmit.append(task["msg_id"])

        # resubmit all msg_ids at once
        try:
            async_results = self.ip_client.resubmit(tasks_to_resubmit)
        except Exception as e:
            print("ERROR: " + str(e))

        # IPython seems to give out new msg_ids instead of re-using the old ones
        for msg_id in async_results.msg_ids:
            print("got new msg_id: " + msg_id)

        # delete old tasks which now have a resubmitted clone
        try:
            self.ip_client.purge_results(tasks_to_resubmit)
        except Exception as e:
            print("ERROR: " + str(e))

        # kickstart all computers
        running_engines = []
        for task in tasks:
            stats = self.ip_client.queue_status('all', True)
            # check if tasks is already running on an engine
            for key,status in list(stats.items()):
                if ('tasks' in status) and (task['msg_id'] in status['tasks']):
                    running_engines.append(key)
        # stop all engines which still run a task
        # the slave wrapper will restart the engine
        running_engines = set(running_engines)
        for engine_id in running_engines:
            self.engine_stop(engine_id)

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
                if 'result_content' in list(task.keys()):
                    result_content = task['result_content']
                    # look for done tasks
                    if ('status' in list(result_content.keys())) and (result_content['status'] == "ok"):
                        status_ok += 1
                    # look for aborted tasks
                    elif ('status' in list(result_content.keys())) and (result_content['status'] == "aborted"):
                        status_aborted += 1
                    # look for done tasks
                    elif ('status' in list(result_content.keys())) and (result_content['status'] == "resubmitted"):
                        status_resubmitted += 1
                    # look for tasks with error
                    elif ('status' in list(result_content.keys())) and (result_content['status'] == "error"):
                        status_error += 1
                    else:
                        status_unknown += 1
        # if at least 1 task is ok, job status is ok
        if status_ok > 0:
            status = "ok"
        # if at least 1 task has unknown status, job status is unknown
        if status_unknown > 0:
            status = "unknown"
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
            sum_times_secs = sum_times.days * 86400 + sum_times.seconds
            meantime_secs = sum_times_secs / len(spent_times)
            meantime = datetime.timedelta(0, meantime_secs)
            # calculate estimated time left
            tasks_left = len(tasks) - len(spent_times)
            time_left = tasks_left * meantime
            # query job object
            job = self.query_job_by_id(job_id)
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
        DrQueueComputer.delete_from_db_by_engine_id(engine_id)
        # we stop the engine
        try:
            self.ip_client.shutdown(engine_id, False, False, True)
        except Exception:
            return False
        return True




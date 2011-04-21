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
        tasks = list()
        task_frames = range(int(job['startframe']), int(job['endframe'])+1, int(job['blocksize']))
    
        for x in task_frames:
            # prepare script input
            env_dict = {
            'DRQUEUE_OS' : DrQueue.get_osname(),
            'DRQUEUE_ETC' : os.getenv('DRQUEUE_ROOT') + "/etc",
            'DRQUEUE_FRAME' : x,
            'DRQUEUE_BLOCKSIZE' : int(job['blocksize']),
            'DRQUEUE_ENDFRAME' : int(job['endframe']),
            'SCENE' : job['scene'],
            'RENDER_TYPE' : "animation"
            }
    
            # run task on cluster
            render_script = os.getenv('DRQUEUE_ROOT') + "/etc/" + DrQueue.get_rendertemplate(job['renderer'])
            ar = self.lbview.apply(DrQueue.run_script_with_env, render_script, env_dict)
            job['tasks'].append(ar)
    
        # make dummy task depend on the others
        # we will track this one like a job
        self.lbview.set_flags(after=tasks)
        job['dummy_task'] = self.lbview.apply(DrQueue.run_dummy)

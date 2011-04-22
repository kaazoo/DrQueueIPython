# -*- coding: utf-8 -*-

"""DrQueue module"""

from client import Client
from job import Job

import platform


def get_rendertemplate(renderer):
    filename = ""
    if renderer == 'blender':
        filename = 'blender_sg.py'
    if renderer == 'maya':
        filename = 'maya_sg.py'
    if renderer == 'mentalray':
        filename = 'mentalray_sg.py'
    return filename 


def get_osname():
    osname = platform.system()
    if osname == 'Darwin':
        osname = 'OSX'
    return osname


def run_script_with_env(script, env_dict):
    DRQUEUE_OS = env_dict['DRQUEUE_OS']
    DRQUEUE_ETC = env_dict['DRQUEUE_ETC']
    DRQUEUE_FRAME = env_dict['DRQUEUE_FRAME']
    DRQUEUE_BLOCKSIZE = env_dict['DRQUEUE_BLOCKSIZE']
    DRQUEUE_ENDFRAME = env_dict['DRQUEUE_ENDFRAME']
    SCENE = env_dict['SCENE']
    RENDER_TYPE = env_dict['RENDER_TYPE']
    return execfile(script)


def run_dummy():
    import time
    time.sleep(1)
    return True
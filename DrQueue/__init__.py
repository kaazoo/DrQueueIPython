# -*- coding: utf-8 -*-

"""
DrQueue main module
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""


import platform
import os
import sys
from client import Client
from job import Job
from computer import Computer
from computer_pool import ComputerPool

supported_renderers = ['3delight', '3dsmax', 'aftereffects', 'aqsis', 'blender', 'cinema4d', 'general', 'lightwave', 'luxrender', 'mantra', 'maya', 'mentalray', 'nuke', 'shake', 'terragen', 'turtle', 'vray', 'xsi']

supported_os = ['Windows', 'Mac OSX', 'Linux', 'FreeBSD', 'NetBSD', 'OpenBSD', 'AIX', 'Solaris']

# check DrQueue environment
if os.getenv('DRQUEUE_ROOT') is None:
    raise ValueError("DRQUEUE_ROOT environment variable not set")


def check_renderer_support(renderer):
    """Check if renderer is supported."""
    if renderer in supported_renderers:
        return True
    else:
        return False

def get_rendertemplate(renderer):
    """Return template filename from renderer name"""
    filename = ""
    if renderer == '3delight':
        filename = '3delight_sg.py'
    if renderer == '3dsmax':
        filename = '3dsmax_sg.py'
    if renderer == 'aftereffects':
        filename = 'aftereffects_sg.py'
    if renderer == 'aqsis':
        filename = 'aqsis_sg.py'
    if renderer == 'blender':
        filename = 'blender_sg.py'
    if renderer == 'cinema4d':
        filename = 'cinema4d_sg.py'
    if renderer == 'general':
        filename = 'general_sg.py'
    if renderer == 'lightwave':
        filename = 'lightwave_sg.py'
    if renderer == 'luxrender':
        filename = 'luxrender_sg.py'
    if renderer == 'mantra':
        filename = 'mantra_sg.py'
    if renderer == 'maya':
        filename = 'maya_sg.py'
    if renderer == 'mentalray':
        filename = 'mentalray_sg.py'
    if renderer == 'nuke':
        filename = 'nuke_sg.py'
    if renderer == 'pixie':
        filename = 'pixie_sg.py'
    if renderer == 'shake':
        filename = 'shake_sg.py'
    if renderer == 'terragen':
        filename = 'terragen_sg.py'
    if renderer == 'turtle':
        filename = 'turtle_sg.py'
    if renderer == 'vray':
        filename = 'vray_sg.py'
    if renderer == 'xsi':
        filename = 'xsi_sg.py'
    return filename 


def get_osname():
    """Return operating system name"""
    osname = platform.system()
    if osname == 'Darwin':
        osname = 'Mac OSX'
    return osname


def run_script_with_env(render_script, env_dict):
    """Run template script on IPython engine"""
    import platform, os, sys
    # set some variables on target machine
    env_dict['DRQUEUE_OS'] = platform.system()
    env_dict['DRQUEUE_ETC'] = os.path.join(os.getenv('DRQUEUE_ROOT'), "etc")
    env_dict['DRQUEUE_LOGFILE'] = os.path.join(os.getenv('DRQUEUE_ROOT'), "logs", env_dict['DRQUEUE_LOGFILE'])
    # import specific render template
    sys.path.append(env_dict['DRQUEUE_ETC'])
    exec("import " + render_script.replace('.py', '') + " as template")
    # run template with env_dict
    status = template.run_renderer(env_dict)
    return status




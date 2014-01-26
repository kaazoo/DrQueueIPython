# -*- coding: utf-8 -*-

"""
DrQueue main module
Copyright (C) 2011-2013 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""


import platform
import os
import sys
import smtplib
import json
from email.mime.text import MIMEText
from .client import Client
from .job import Job
from .computer import Computer


supported_renderers = ['3delight', '3dsmax', 'aftereffects', 'aqsis', \
'blender', 'cinema4d', 'general', 'lightwave', 'luxrender', 'mantra', \
'maya', 'mentalray', 'nuke', 'shake', 'terragen', 'turtle', 'vray', 'xsi']

supported_os = ['Windows', 'Mac OSX', 'Linux', 'FreeBSD', 'NetBSD', 'OpenBSD', \
'AIX', 'Solaris']


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
    env_dict['DRQUEUE_LOGFILE'] = os.path.join(os.getenv('DRQUEUE_ROOT'),
        "logs", env_dict['DRQUEUE_LOGFILE'])
    # import specific render template
    sys.path.append(env_dict['DRQUEUE_ETC'])
    impmod = render_script.replace('.py', '')
    __import__(impmod)
    template = sys.modules[impmod]
    # run template with env_dict
    status = template.run_renderer(env_dict)
    return status


def check_deps(dep_dict):
    """Run all dependency checking functions.  This method runs directly on the engine."""
    if ('os_name' in dep_dict) and (engine_has_os(dep_dict['os_name']) == False):
        return False
    elif ('minram' in dep_dict) and (engine_has_minram(dep_dict['minram']) == False):
        return False
    elif ('mincores' in dep_dict) and (engine_has_mincores(dep_dict['mincores']) == False):
        return False
    elif ('pool_name' in dep_dict) and (engine_is_in_pool(dep_dict['pool_name']) == False):
        return False
    elif ('job_id' in dep_dict) and (job_is_enabled(dep_dict['job_id']) == False):
        return False
    else:
        return True


def engine_is_in_pool(pool_name):
    """Check if engine belongs to certain pool. This method runs directly on the engine."""

    # check os.environ["DRQUEUE_POOL"]
    if ("DRQUEUE_POOL" in os.environ) and (pool_name in os.environ["DRQUEUE_POOL"]):
        return True
    else:
        return False


def engine_has_os(os_name):
    """Check if engine is running on certain OS. This method runs directly on the engine."""
    running_os = get_osname()
    if os_name == running_os:
        return True
    else:
        return False


def engine_has_minram(minram):
    """Check if engine has at least minram GB RAM. This method runs directly on the engine."""
    mem = Computer.get_memory()
    if mem >= minram:
        return True
    else:
        return False


def engine_has_mincores(mincores):
    """Check if engine has at least mincores CPU cores. This method runs directly on the engine."""
    ncpus = Computer.get_ncpus()
    ncorescpu = Computer.get_ncorescpu()
    cores = ncpus * ncorescpu
    if cores >= mincores:
        return True
    else:
        return False


def job_is_enabled(job_id):
    """Check if job is enabled. This method runs directly on the engine."""
    job = Job.query_db(job_id)
    if (job != None) and (job["enabled"] == True):
        return True
    else:
        return False


def send_email(job_name, recipients):
    """Notify recipients about finish of job."""
    # load email configuration
    user_dir = os.path.expanduser("~")
    config_file = os.path.join(user_dir, ".drqueue", "email_config.json")
    try:
        fp = open(config_file, "rb")
    except:
        print("Email configuration could not be loaded.")
    try:
        config = json.load(fp)
    except:
        print("Email configuration could not be parsed.")
    print(config)
    mail_from = config['from']
    body_text = "Your render job \"%s\" is finished." % job_name
    # Create a text/plain message
    msg = MIMEText(body_text)
    # subject, sender and recipients
    msg['Subject'] = "Job \"%s\" is finished" % job_name
    msg['From'] = mail_from
    msg['To'] = recipients
    if config['smtp_ssl'] == "1":
        # connect via SSL
        smtp = smtplib.SMTP_SSL(config['smtp_server'], int(config['smtp_port']))
    else:
        # connect without SSL
        smtp = smtplib.SMTP(config['smtp_server'], int(config['smtp_port']))
        # start TLS encryption
        if config['smtp_tls'] == "1":
            smtp.starttls()
    if config['smtp_auth'] == "1":
        # authenticate if required
        smtp.login(config['smtp_user'], config['smtp_passwd'])
    try:
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
    except:
        print("Email could not be sent.")
    smtp.quit()


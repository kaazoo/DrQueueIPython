# -*- coding: utf-8 -*-

"""
DrQueue Job submodule
Copyright (C) 2011,2012 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os
import datetime
import getpass

import pymongo
import bson

import DrQueue


def connect_db():
    """ 
    :return: MongoDB connection object
    """
    host=os.getenv('DRQUEUE_MONGODB', None)
    if not host:
        raise RuntimeError("Error: DRQUEUE_MONGODB not set!")
    
    print("Connect MongoDB on %s" % host)
    connection = pymongo.Connection(host)
    db = connection['ipythondb']
    return db


def get_jobs():
    """
    :return: return 'drqueue_jobs'
    """
    db = connect_db()
    jobs = db['drqueue_jobs']
    return jobs


class Job(dict):
    """Subclass of dict for collecting Job attribute values."""
    def __init__(self, name, startframe, endframe, blocksize, renderer, scenefile, retries=1, owner=getpass.getuser(), options={}, created_with=None, limits={}):
        dict.__init__(self)
        # mandatory elements
        jb = {'name' : name,
              'startframe' : int(startframe),
              'endframe' : int(endframe),
              'blocksize' : int(blocksize),
              'renderer' : renderer,
              'scenefile' : scenefile,
              'retries' : int(retries),
              'owner' : owner,
              'submit_time' : datetime.datetime.now(),
              'requeue_time' : False,
              'created_with' : created_with,
              'enabled' : True,
              'limits' : {}
             }

        if name == "":
            raise ValueError("No name of job given!")
        if not (endframe > startframe):
            raise ValueError("Endframe must be bigger than startframe!")
        if blocksize < 1:
            raise ValueError("Blocksize needs to be at least 1!")
        if DrQueue.check_renderer_support(renderer) == False:
            raise ValueError("Render called \"%s\" not supported!" % renderer)
        if scenefile == "":
            raise ValueError("No scenefile given!")

        # optional elements
        if 'renderdir' in options:
            jb['renderdir'] = options['renderdir']
        if 'projectdir' in options:
            jb['projectdir'] = options['projectdir']
        if 'configdir' in options:
            jb['configdir'] = options['configdir']
        if 'imagefile' in options:
            jb['imagefile'] = options['imagefile']
        if 'precommand' in options:
            jb['precommand'] = options['precommand']
        if 'postcommand' in options:
            jb['postcommand'] = options['postcommand']
        if 'viewcommand' in options:
            jb['viewcommand'] = options['viewcommand']
        if 'worldfile' in options:
            jb['worldfile'] = options['worldfile']
        if 'terrainfile' in options:
            jb['terrainfile'] = options['terrainfile']
        if 'composition' in options:
            jb['composition'] = options['composition']
        if 'camera' in options:
            jb['camera'] = options['camera']
        if 'resx' in options:
            jb['resx'] = options['resx']
        if 'resy' in options:
            jb['resy'] = options['resy']
        if 'renderpass' in options:
            jb['renderpass'] = options['renderpass']
        if 'rendertype' in options:
            jb['rendertype'] = options['rendertype']
        if 'fileextension' in options:
            jb['fileextension'] = options['fileextension']
        if 'send_email' in options:
            jb['send_email'] = options['send_email']
        if 'email_recipients' in options:
            jb['email_recipients'] = options['email_recipients']
        if 'custom_command' in options:
            jb['custom_command'] = options['custom_command']
        # limits
        if 'os' in limits:
            jb['limits']['os'] = limits['os']
        if 'depend' in limits:
            jb['limits']['depend'] = limits['depend']
        if 'minram' in limits:
            jb['limits']['minram'] = limits['minram']
        if 'mincores' in limits:
            jb['limits']['mincores'] = limits['mincores']
        if 'pool_name' in limits:
            jb['limits']['pool_name'] = limits['pool_name']

        self.update(jb)


    @staticmethod
    def store_db(job):
        """store job information in MongoDB"""
        jobs = get_jobs()
        job_id = jobs.insert(job)
        job['_id'] = str(job['_id'])
        return job_id


    @staticmethod
    def update_db(job):
        """update job information in MongoDB"""
        jobs = get_jobs()
        job_id = jobs.save(job)
        job['_id'] = str(job['_id'])
        return job_id


    @staticmethod
    def query_db(job_id):
        """query job information from MongoDB"""
        jobs = get_jobs()
        try:
            job = jobs.find_one({"_id": bson.ObjectId(job_id)})
        except bson.errors.InvalidId:
            print("Format error: Invalid BSON.")
            job = None
        return job


    @staticmethod
    def delete_from_db(job_id):
        """query job information from MongoDB"""
        jobs = get_jobs()
        return jobs.remove({"_id": bson.ObjectId(job_id)})


    @staticmethod
    def query_jobnames():
        """query job names from MongoDB"""
        jobs = get_jobs()
        names = []
        for job in jobs.find():
            names.append(job['name'])
        return names


    @staticmethod
    def query_job_by_name(job_name):
        """query job information from MongoDB by name"""
        jobs = get_jobs()
        job = jobs.find_one({"name": job_name})
        return job


    @staticmethod
    def query_job_list():
        """query list of jobs from MongoDB"""
        jobs = get_jobs()
        return list(jobs.find())
        

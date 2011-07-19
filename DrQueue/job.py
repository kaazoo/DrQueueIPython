# -*- coding: utf-8 -*-

"""
DrQueue Job submodule
Copyright (C) 2011 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os
import getpass
import pymongo
import bson


class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable


class Job(dict):
    """Subclass of dict for collecting Job attribute values."""
    def __init__(self, name, startframe, endframe, blocksize, renderer, scenefile, retries=1, owner=getpass.getuser(), pool=None, options={}):
        dict.__init__(self)
        # mandatory elements
        jb = {'name' : name,
              'startframe' : startframe,
              'endframe' : endframe,
              'blocksize' : blocksize,
              'renderer' : renderer,
              'scenefile' : scenefile,
              'retries' : retries,
              'owner' : owner,
              'pool' : pool
             }
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
        self.update(jb)


    def store_db(job):
        """store job information in MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        jobs = db['drqueue_jobs']
        job_id = jobs.insert(job)
        job['_id'] = str(job['_id'])
        return job_id
    store_db = Callable(store_db)


    def query_db(job_id):
        """query job information from MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        jobs = db['drqueue_jobs']
        job = jobs.find_one({"_id": bson.ObjectId(job_id)})
        return job
    query_db = Callable(query_db)


    def delete_from_db(job_id):
        """query job information from MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        jobs = db['drqueue_jobs']
        return jobs.remove({"_id": bson.ObjectId(job_id)})
    delete_from_db = Callable(delete_from_db)


    def query_jobnames():
        """query job names from MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        jobs = db['drqueue_jobs']
        names = []
        for job in jobs.find():
            names.append(job['name'])
        return names
    query_jobnames = Callable(query_jobnames)


    def query_job_by_name(job_name):
        """query job information from MongoDB by name"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        jobs = db['drqueue_jobs']
        job = jobs.find_one({"name": job_name})
        return job
    query_job_by_name = Callable(query_job_by_name)


    def query_job_list():
        """query list of jobs from MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        jobs = db['drqueue_jobs']
        job_arr = []
        for job in jobs.find():
            job_arr.append(job)
        return job_arr
    query_job_list = Callable(query_job_list)
        

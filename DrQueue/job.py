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
    def __init__(self, name, startframe, endframe, blocksize, renderer, scenefile, retries=1, owner=getpass.getuser(), options={}):
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


    def save_to_db(job):
        """store job information in MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        jobs = db['drqueue_jobs']
        return jobs.insert(job)
    save_to_db = Callable(save_to_db)


    def get_from_db(job_id):
        """get job information from MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        jobs = db['drqueue_jobs']
        job = jobs.find_one({"_id": bson.ObjectId(job_id)})
        return job
    get_from_db = Callable(get_from_db)

        

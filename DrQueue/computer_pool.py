# -*- coding: utf-8 -*-

"""
DrQueue ComputerPool submodule
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


class ComputerPool(dict):
    """Subclass of dict for collecting Pool attribute values."""
    def __init__(self, name, engine_ids={}):
        dict.__init__(self)
        # mandatory elements
        pool = {
              'name' : name,
              'engine_ids' : engine_ids,
             }
        self.update(pool)


    def store_db(pool):
        """store pool information in MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool_id = jobs.insert(pool)
        pool['_id'] = str(pool['_id'])
        return pool_id
    store_db = Callable(store_db)


    def query_db(pool_id):
        """query pool information from MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool = pools.find_one({"_id": bson.ObjectId(pool_id)})
        return pool
    query_db = Callable(query_db)


    def delete_from_db(pool_id):
        """delete pool information from MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        return pools.remove({"_id": bson.ObjectId(pool_id)})
    delete_from_db = Callable(delete_from_db)


    def query_poolnames():
        """query pool names from MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        names = []
        for pool in pools.find():
            names.append(pool['name'])
        return names
    query_poolnames = Callable(query_poolnames)


    def query_pool_by_name(pool_name):
        """query pool information from MongoDB by name"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool = pools.find_one({"name": pool_name})
        return pool
    query_pool_by_name = Callable(query_pool_by_name)


    def query_pool_list():
        """query list of jobs from MongoDB"""
        connection = pymongo.Connection()
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool_arr = []
        for pool in pools.find():
            pool_arr.append(pool)
        return pool_arr
    query_pool_list = Callable(query_pool_list)
        

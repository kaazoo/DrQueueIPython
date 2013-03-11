# -*- coding: utf-8 -*-

"""
DrQueue ComputerPool submodule
Copyright (C) 2011,2012 Andreas Schroeder

This file is part of DrQueue.

Licensed under GNU General Public License version 3. See LICENSE for details.
"""

import os
import getpass


class ComputerPool(dict):
    """Subclass of dict for collecting Pool attribute values."""
    def __init__(self, name, engine_names=[]):
        dict.__init__(self)

        if type(engine_names).__name__ != 'list':
            raise ValueError("argument is not of type list")
            return False

        # mandatory elements
        pool = {
              'name' : name,
              'engine_names' : engine_names,
             }
        self.update(pool)


    @staticmethod
    def store_db(pool):
        import pymongo
        """store pool information in MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MONGODB'))
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool_id = pools.insert(pool)
        pool['_id'] = str(pool['_id'])
        return pool_id


    @staticmethod
    def update_db(pool):
        import pymongo
        """update pool information in MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MONGODB'))
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool_id = pools.save(pool)
        pool['_id'] = str(pool['_id'])
        return pool_id


    @staticmethod
    def query_db(pool_id):
        import pymongo
        import bson
        """query pool information from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MONGODB'))
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool = pools.find_one({"_id": bson.ObjectId(pool_id)})
        return pool


    @staticmethod
    def delete_from_db(pool_id):
        import pymongo
        import bson
        """delete pool information from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MONGODB'))
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        return pools.remove({"_id": bson.ObjectId(pool_id)})


    @staticmethod
    def query_poolnames():
        import pymongo
        """query pool names from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MONGODB'))
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        names = []
        for pool in pools.find():
            names.append(pool['name'])
        return names


    @staticmethod
    def query_pool_by_name(pool_name):
        import pymongo
        """query pool information from MongoDB by name"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MONGODB'))
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool = pools.find_one({"name": pool_name})
        return pool


    @staticmethod
    def query_pool_list():
        import pymongo
        """query list of pools from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MONGODB'))
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool_arr = []
        for pool in pools.find():
            pool_arr.append(pool)
        return pool_arr
        

    @staticmethod
    def query_pool_members(pool_name):
        import pymongo
        """query list of members of pool from MongoDB"""
        connection = pymongo.Connection(os.getenv('DRQUEUE_MONGODB'))
        db = connection['ipythondb']
        pools = db['drqueue_pools']
        pool = pools.find_one({"name": pool_name})
        if pool == None:
            return None
        else:
            return list(pool['engine_names'])


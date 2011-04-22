# -*- coding: utf-8 -*-

import os

class Job(dict):
    """Subclass of dict for Jobs."""
    def __init__(self, startframe, endframe, blocksize, scene, renderer):
        dict.__init__(self)
        jb = {'startframe' : startframe,
              'blocksize' : blocksize,
              'endframe' : endframe,
              'scene' : scene,
              'renderer' : renderer,
              'tasks' : [],
              'dummy_task' : None,
             }
        self.update(jb)
                
        

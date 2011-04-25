# -*- coding: utf-8 -*-

import os

class Job(dict):
    """Subclass of dict for Jobs."""
    def __init__(self, name, startframe, endframe, blocksize, scene, renderer):
        dict.__init__(self)
        jb = {'name' : name,
              'startframe' : startframe,
              'blocksize' : blocksize,
              'endframe' : endframe,
              'scene' : scene,
              'renderer' : renderer,
             }
        self.update(jb)
                
        

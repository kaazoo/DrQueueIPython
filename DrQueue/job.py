# -*- coding: utf-8 -*-

import os

class Job(dict):
    """Subclass of dict for Jobs."""
    def __init__(self, name, startframe, endframe, blocksize, renderer, scenefile, options={}):
        dict.__init__(self)
        # mandatory elements
        jb = {'name' : name,
              'startframe' : startframe,
              'blocksize' : blocksize,
              'endframe' : endframe,
              'renderer' : renderer,
              'scenefile' : scenefile,
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
                
        

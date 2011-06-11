DrQueueIPython
==============

This is a port of DrQueue to Python. IPython will be used for network communication and task management.
See more information https://ssl.drqueue.org/redmine/projects/drqueueipython

DrQueue has been created by Jorge Daza Garcia-Blanes. See http://www.drqueue.org for more information.


Design changes
--------------

* Master becomes IPController
* Slave becomes IPEngine
* Clients can use the IPython.parallel.Client class to talk to IPController
* No compiling needed anymore. Just Python code.
* IPython and MongoDB become dependencies.
* MongoDB is be used for job/task information storage.
* There is no direct access to frame information anymore. Jobs can be devided into tasks. Depending on the blocksize, one task can consist of one or more frames.
* High water mark (HWM) can be set for IPEngines in order to always keep some tasks for late joining engines.


Test setup
----------

* install ZMQ 2.1.4 and pyzmq 2.1.4
* install Git version of IPython 0.11dev from https://github.com/ipython/ipython
* install MongoDB and PyMongo
* edit ~/.config/ipython/cluster_default/ipcontroller_config.py:
  c.HubFactory.db_class = 'IPython.parallel.controller.mongodb.MongoDB'
  c.MongoDB.database = 'ipythondb'
  c.TaskScheduler.hwm = 2
* run MongoDB server: "mongod --dbpath ~/.config/ipython/db/"
* run IPController: "ipcontroller"
* run several IPEngines: "ipengine"
* submit some tasks:
  python2.6 sendjob_ipython.py -s 1 -e 3 -b 1 -r blender -f /usr/local/drqueue/tmp/icetest.blend -n "Job 123" -o "{'rendertype':'animation'}" -w -v
* list known jobs and their tasks: "python2.6 listjobs_ipython.py"


Support development
-------------------

[![Flattr Button](http://api.flattr.com/button/button-static-50x60.png "Flattr This!")](http://flattr.com/thing/181901/DrQueueIPython-project "DrQueueIPython project")


License
-------

Copyright (C) 2011 Andreas Schroeder

Licensed under GNU General Public License version 3. See LICENSE for details.
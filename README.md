DrQueueIPython
==============

This is a port of DrQueue to Python. IPython is used for network communication and task management.
See more information at https://ssl.drqueue.org/redmine/projects/drqueueipython .

DrQueue has been created by Jorge Daza Garcia-Blanes. See http://www.drqueue.org for more information.


Design changes
--------------

* Master runs IPController
* Slave runs IPEngine
* Clients can use the IPython.parallel.Client class to talk to IPController
* No compiling needed anymore. Just Python code.
* ZMQ, PyZMQ, MongoDB, PyMongo and IPython become dependencies.
* MongoDB is be used for information storage of tasks, jobs, pools, ... .
* There is no direct access to frame information anymore. Jobs can be devided into tasks. Depending on the blocksize, one task can consist of one or more frames.
* High water mark (HWM) can be set for IPEngines in order to control how many tasks are queued to each engine and to always keep some tasks for late joining engines.
* DrQueueIPython provides a Python module for easy accces to the underlying technology. This makes integration into other software which uses Python possible.


Requirements
------------

* ZMQ >= 2.1.4 and pyzmq >= 2.1.4 from http://www.zeromq.org
* IPython 0.11 from http://www.ipython.org
* MongoDB >= 1.8 and PyMongo >= 1.10 from http://www.mongodb.org


Installation
------------

* Run "python setup.py install" to install DrQueue module and scripts.
* For more information, see the DrQueueIPython wiki at https://ssl.drqueue.org/redmine/projects/drqueueipython/wiki .


Support development
-------------------

[![Flattr Button](http://api.flattr.com/button/button-static-50x60.png "Flattr This!")](http://flattr.com/thing/181901/DrQueueIPython-project "DrQueueIPython project")


License
-------

Copyright (C) 2011 Andreas Schroeder

Licensed under GNU General Public License version 3. See LICENSE for details.


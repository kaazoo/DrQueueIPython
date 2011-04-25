
This is going to become a rewrite of DrQueue in Python. IPython will be used for network communication and task management.


Design changes:

* Master becomes IPController
* Slave becomes IPEngine
* Clients can use the IPython.parallel.Client class to talk to IPController
* No compiling needed anymore. Just Python code.
* IPython becomes a dependency.
* SQLite or MongoDB can be used for job/task information storage.
* There is no direct access to frame information anymore. Jobs can be devided into tasks. Depending on the blocksize, one task can consist of one or more frames.
* High water mark (HWM) can be set for IPEngines in order to always keep some tasks for late joining engines.


Current problems:

* IPython can't group tasks to jobs. So far we'll use the session name for the job name as a workaround.
* Ruby clients (DrQueueRubyBindings) will have to use a Web API or some kind of wrapper to be able to call Python code.
* The terminal output is not yet piped into a logfile or a Python variable.
* There is not yet a way to group several computers to pools.
* It's unclear how to continue stopped jobs/tasks.
* It's unclear how to define the number of times a task should be requeued.


Test setup:
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
* submit some tasks: "python2.6 sendjob_ipython.py -s 1 -e 20 -b 3 -r blender -f /usr/local/drqueue/tmp/icetest.blend -w -v"
* list known jobs and their tasks: "python2.6 listjobs_ipython.py"


TODO:

* Enhance Job and Client classes.
* Add utility functions to DrQueue module.



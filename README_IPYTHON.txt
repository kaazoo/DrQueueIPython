
This is going to become a rewrite of DrQueue in Python. IPython will be used for network communication and task management.


Design changes:

* Master becomes ipcontroller
* Slave becomes ipengine
* Clients can use the IPython.parallel.Client class to talk to ipcontroller
* No compiling needed anymore. Just Python code.
* IPython becomes a dependency.
* SQLite or MongoDB can be used for job/task information storage.
* There is no direct access to frame information anymore. Jobs can be devided into tasks. Depending on the blocksize, one task can consist of one or more frames.

Current problems:

* IPython can't group tasks to jobs. So far we'll use dependent pseudo tasks as a workaround.
* Ruby clients (DrQueueRubyBindings) will have to use a Web API or some kind of wrapper to be able to call Python code.
* The terminal output is not yet piped into a logfile or a Python variable.
* There is not yet a way to group several computers to pools.
* Tasks are very early bound to existing engines. Engines which join later don't get any of the queued tasks.
* It's unclear how to continue stopped jobs/tasks.

TODO:

* Create the classes: Job, ...
* Create a DrQueue module

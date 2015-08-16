#!/usr/bin/env python

import os, glob, shutil, sys, pwd, grp
from setuptools import setup
from distutils.core import setup, Command


def read(fname):
    """Read file contents."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def recursive_chown(path, uid, gid):
    """Do chown recursively."""
    os.chown(path, uid, gid)
    for item in os.listdir(path):
        itempath = os.path.join(path, item)
        if os.path.isfile(itempath):
            os.chown(itempath, uid, gid)
        elif os.path.isdir(itempath):
            os.chown(itempath, uid, gid)
            recursive_chown(itempath, uid, gid)


class CreateDrQueueWorkDirs(Command):
    """Create working directories for DrQueue."""

    description = "Create working directories for DrQueue."

    bp_option = ("basepath=", None, "Base path for DrQueue work directories. Default is '/usr/local/drqueue'.")
    o_option = ("owner=", None, "Owner for directories.")
    g_option = ("group=", None, "Group for directories.")
    user_options = [bp_option, o_option, g_option]
    boolean_options = []

    def initialize_options(self):
        self._dir = os.getcwd()
        self.basepath = None
        self.owner = None
        self.group = None

    def finalize_options(self):
        pass

    def run(self):
        # set to user-supplied path is available
        if self.basepath != None:
            drqueue_root = self.basepath
        else:
            drqueue_root = "/usr/local/drqueue"

        print("Creating DrQueue work directories in '" + drqueue_root + "'.")

        # create DrQueue directory structure
        if not os.path.exists(drqueue_root):
            os.makedirs(drqueue_root)
        drqueue_etc = os.path.join(drqueue_root, "etc")
        if not os.path.exists(drqueue_etc):
            os.mkdir(drqueue_etc)
        drqueue_logs = os.path.join(drqueue_root, "logs")
        if not os.path.exists(drqueue_logs):
            os.mkdir(drqueue_logs)
        drqueue_tmp = os.path.join(drqueue_root, "tmp")
        if not os.path.exists(drqueue_tmp):
            os.mkdir(drqueue_tmp)

        # create IPython subdirectories
        drqueue_ipython = os.path.join(drqueue_root, 'ipython')
        if not os.path.exists(drqueue_ipython):
            os.mkdir(drqueue_ipython)
        drqueue_ipython_db = os.path.join(drqueue_ipython, 'db')
        if not os.path.exists(drqueue_ipython_db):
            os.mkdir(drqueue_ipython_db)
        drqueue_ipython_profile = os.path.join(drqueue_ipython, 'profile_default')
        if not os.path.exists(drqueue_ipython_profile):
            os.mkdir(drqueue_ipython_profile)
        drqueue_ipython_profile_log = os.path.join(drqueue_ipython_profile, 'log')
        if not os.path.exists(drqueue_ipython_profile_log):
            os.mkdir(drqueue_ipython_profile_log)
        drqueue_ipython_profile_pid = os.path.join(drqueue_ipython_profile, 'pid')
        if not os.path.exists(drqueue_ipython_profile_pid):
            os.mkdir(drqueue_ipython_profile_pid)
        drqueue_ipython_profile_security = os.path.join(drqueue_ipython_profile, 'security')
        if not os.path.exists(drqueue_ipython_profile_security):
            os.mkdir(drqueue_ipython_profile_security)
        drqueue_ipython_profile_startup = os.path.join(drqueue_ipython_profile, 'startup')
        if not os.path.exists(drqueue_ipython_profile_startup):
            os.mkdir(drqueue_ipython_profile_startup)

        # copy template files
        templates = os.path.join(self._dir, "etc", "*.py")
        for template in glob.glob(templates):
            shutil.copy(template, drqueue_etc)

        # Windows lacks Unix functionality
        if not sys.platform.startswith("win"):
            # set to user-supplied user / group
            if self.owner != None:
                uid = pwd.getpwnam(self.owner)[2]
                recursive_chown(drqueue_root, uid, -1)
            if self.group != None:
                gid = grp.getgrnam(self.group)[2]
                recursive_chown(drqueue_root, -1, gid)

        print("\nAdd the following environment variables to your user profile:")
        print("DRQUEUE_ROOT=" + drqueue_root)
        print("IPYTHONDIR=" + drqueue_ipython)


# register extra command
cmdclass = {'create_drqueue_dirs': CreateDrQueueWorkDirs}
allscripts = []
allscripts.append(os.path.join('bin', 'drqueue'))
allscripts.append(os.path.join('bin', 'get_slave_information.py'))

setup(
    name = "DrQueueIPython",
    version = "0.2.1",
    author = "Andreas Schroeder",
    author_email = "andreas@drqueue.org",
    description = ("This is a port of DrQueue to Python. IPython is used for network communication and task management."),
    license = "GPLv3",
    keywords = "render renderfarm management drqueue",
    url = "https://ssl.drqueue.org/redmine/projects/drqueueipython",
    packages = ['DrQueue'],
    scripts = allscripts,
    install_requires = [
        'ipython<3', # TODO: upgrade to newest ipython version
        'pyzmq>=2.1.4',
        'pymongo<3', # TODO: upgrade to newest pymongo version
        'psutil>=3.1.1'
    ],
    long_description = read('README.md'),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    cmdclass = cmdclass,
    zip_safe = False
)

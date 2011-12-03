import ez_setup
ez_setup.use_setuptools()

import os, glob, shutil, sys
from setuptools import setup
from distutils.core import setup, Command


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class CreateDrQueueWorkDirs(Command):
    """Create working directories for DrQueue."""

    description = "Create working directories for DrQueue."

    user_options = []
    boolean_options = []

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        if sys.platform.startswith('win'):
            print("Sorry, but creating paths on Windows is curently not supported.")
            sys.exit(1)

        drqueue_root = "/usr/local/drqueue"

        print("Creating DrQueue work directories in " + drqueue_root + ".")

        if not os.path.exists(drqueue_root):
            os.makedirs(drqueue_root)
        drqueue_etc = os.path.join(drqueue_root, "etc")
        if not os.path.exists(drqueue_etc):
            os.mkdir(drqueue_etc)
        drqueue_ipython = os.path.join(drqueue_root, "ipython")
        if not os.path.exists(drqueue_ipython):
            os.mkdir(drqueue_ipython)
        drqueue_logs = os.path.join(drqueue_root, "logs")
        if not os.path.exists(drqueue_logs):
            os.mkdir(drqueue_logs)
        drqueue_tmp = os.path.join(drqueue_root, "tmp")
        if not os.path.exists(drqueue_tmp):
            os.mkdir(drqueue_tmp)

        templates = os.path.join(self._dir, "etc", "*.py")
        for template in glob.glob(templates):
            shutil.copy(template, drqueue_etc)

        print("\nAdd the following environment variables to your user profile:")
        print("DRQUEUE_ROOT=" + drqueue_root)
        print("IPYTHON_DIR=" + drqueue_ipython)


cmdclass = {'create_drqueue_dirs': CreateDrQueueWorkDirs}


setup(
    name = "DrQueueIPython",
    version = "0.1",
    author = "Andreas Schroeder",
    author_email = "andreas@drqueue.org",
    description = ("This is a port of DrQueue to Python. IPython is used for network communication and task management."),
    license = "GPLv3",
    keywords = "render renderfarm management drqueue",
    url = "https://ssl.drqueue.org/redmine/projects/drqueueipython",
    packages = ['DrQueue'],
    scripts = glob.glob(os.path.join('bin', '*.py')),
    install_requires = ['ipython>=0.11', 'pyzmq>=2.1.4'],
    long_description = read('README.md'),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GPLv3 License",
    ],
    cmdclass = cmdclass
)

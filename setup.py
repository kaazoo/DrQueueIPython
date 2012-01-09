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

        # Windows lacks Unix functionality
        if sys.platform.startswith("win"):
            print("Sorry, but creating paths on Windows is curently not supported.")
            sys.exit(1)

        # set to user-supplied path is available
        if self.basepath != None:
            drqueue_root = self.basepath
        else:
            drqueue_root = "/usr/local/drqueue"

        print("Creating DrQueue work directories in '" + drqueue_root + "'.")

        # create directory structure
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

        # copy template files
        templates = os.path.join(self._dir, "etc", "*.py")
        for template in glob.glob(templates):
            shutil.copy(template, drqueue_etc)

        # set to user-supplied user / group
        if self.owner != None:
            uid = pwd.getpwnam(self.owner)[2]
            recursive_chown(drqueue_root, uid, -1)
        if self.group != None:
            gid = grp.getgrnam(self.group)[2]
            recursive_chown(drqueue_root, -1, gid)

        print("\nAdd the following environment variables to your user profile:")
        print("DRQUEUE_ROOT=" + drqueue_root)
        print("IPYTHON_DIR=" + drqueue_ipython)


# register extra command
cmdclass = {'create_drqueue_dirs': CreateDrQueueWorkDirs}


setup(
    name = "DrQueueIPython",
    version = "0.0.1",
    author = "Andreas Schroeder",
    author_email = "andreas@drqueue.org",
    description = ("This is a port of DrQueue to Python. IPython is used for network communication and task management."),
    license = "GPLv3",
    keywords = "render renderfarm management drqueue",
    url = "https://ssl.drqueue.org/redmine/projects/drqueueipython",
    packages = ['DrQueue'],
    scripts = glob.glob(os.path.join('bin', '*.py')),
    install_requires = ['ipython>=0.12', 'pyzmq>=2.1.4'],
    long_description = read('README.md'),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    cmdclass = cmdclass
)

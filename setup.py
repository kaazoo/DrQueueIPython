import ez_setup
ez_setup.use_setuptools()

import os, glob
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "DrQueueIPython",
    version = "0.1",
    author = "Andreas Schroeder",
    author_email = "andreas@drqueue.org",
    description = ("This is a port of DrQueue to Python. IPython is used for network communication and task management."),
    license = "GPLv3",
    keywords = "render renderfarm management drqueue",
    url = "http://packages.python.org/DrQueueIPython",
    packages = ['DrQueue'],
    scripts = glob.glob(os.path.join('bin', '*.py')),
    install_requires = ['ipython>=0.11', 'pyzmq>=2.1.4'],
    long_description = read('README.md'),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GPLv3 License",
    ],
)

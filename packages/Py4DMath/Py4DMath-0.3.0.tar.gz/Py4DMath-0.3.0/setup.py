from os.path import abspath, dirname, join
from setuptools import find_packages, setup

BASE_DIR = dirname(abspath(__file__))
VERSION_FILE = join(BASE_DIR, 'Py4DMath', 'version.py')

def get_version():
    with open(VERSION_FILE) as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                version = line.split()[-1].strip('"')
                return version
        raise AttributeError("Package does not have a __version__")

setup(
    name='Py4DMath',
    packages=find_packages(include=['Py4DMath']),
    version=get_version(),
    description='A math engine for controlling 3D objects',
    author='Nicholas Chumney',
    license='MIT',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)

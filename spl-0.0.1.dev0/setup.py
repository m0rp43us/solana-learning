from setuptools import setup, find_packages
import re

VERSIONFILE = "src/spl/metadata.py"
verstr = "unknown"

setup(
    name='spl',
    version='0.0.1',
    description='Spigot/Bukkit Plugin Manager',
    author='James Muscat',
    author_email='jamesremuscat@gmail.com',
    url='https://github.com/jamesremuscat/spl',
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir = {'':'src'},
    setup_requires=['nose'],
    tests_require=[],
    install_requires=['bunch', 'cachecontrol[filecache]', 'cfscrape', 'lockfile', 'pyyaml', 'requests', 'simplejson'],
    entry_points={
        'console_scripts': [
            'spl = spl.cli:main',
            ],
        }
      )

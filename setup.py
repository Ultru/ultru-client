#!/usr/bin/env python

#from distutils.core import setup
import os
from setuptools import find_packages, setup
import subprocess


with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "requirements.txt")), "r") as fp:
    requirements = fp.read().split(os.linesep)
    if not isinstance(requirements, list):
        requirements = list()
    requirements = [r for r in requirements if r != '']

setup(name='ultru client',
      description='Query the Ultru API using a simple to use CLI',
      author='Matt',
      author_email='matt@ultru.io',
      package_dir={"": "src"},
      packages=find_packages("src"),
      version_format='{tag}.{commitcount}',
      setup_requires=['setuptools-git-version'],
      python_requires='>=3.6',
      install_requires=requirements,
      classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
      ],
      keywords='ultru query development api',
      project_urls={
        'Signup': 'http://www.ultru.io',
        'Source': 'https://github.com/ultru/ultru-cli/',
      },
      entry_points={'console_scripts': ['ultru-cli=ultru_client.cli:main', 'ultru-shell=ultru_client.shell:main']}
     )
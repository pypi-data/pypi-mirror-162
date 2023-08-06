#!/usr/bin/env python

# Setup file for rest harness

from setuptools import setup
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='rhclient',
      version='0.2.1',
      description='Python REST Service Test utility',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Robbie Reed',
      author_email='robbiereed@psg-inc.net',
      url='https://www.restharness.com',
      package_dir={"": "src"},
      packages=setuptools.find_packages(where="src"),
      python_requires=">=3.6",
      install_requires=['requests']
     )

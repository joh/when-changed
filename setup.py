#!/usr/bin/env python

from setuptools import setup

setup(name='when-changed',
      version='0.2.0',
      description='Run a command when a file is changed',
      author='Johannes H. Jensen',
      url='https://github.com/joh/when-changed',
      packages=['whenchanged'],
      scripts=['when-changed'],
      install_requires=['pyinotify'],
      license='BSD'
      )

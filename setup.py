#!/usr/bin/env python

from distutils.core import setup

setup(  name='When-changed',
        version='0.2.0',
        description='Run a command when a file is changed',
        author='Johannes H. Jensen',
        url='https://github.com/joh/when-changed',
        packages=['whenchanged'],
        scripts=['when-changed'],
        requires=['pyinotify'],
        license = 'BSD'
        )

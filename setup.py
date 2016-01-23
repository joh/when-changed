from setuptools import setup

setup(name='when-changed',
      version='0.3.0',
      description='Run a command when a file is changed',
      author='Johannes H. Jensen',
      author_email='joh@pseudoberries.com',
      url='https://github.com/joh/when-changed',
      packages=['whenchanged'],
      scripts=['when-changed'],
      install_requires=['watchdog'],
      license='BSD'
      )

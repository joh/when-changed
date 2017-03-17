#!/usr/bin/env python
"""%(prog)s - run a command when a file is changed

Usage: %(prog)s [-vr1s] FILE COMMAND...
       %(prog)s [-vr1s] FILE [FILE ...] -c COMMAND
       %(prog)s --help

FILE can be a directory. Use %%f to pass the filename to the command.

Options:
-h, --help  Print this help
-r          Watch recursively
-v          Verbose output
-1          Don't re-run command if files changed while command was running
-s          Run command immediately at start

Copyright (c) 2011-2016, Johannes H. Jensen.
License: BSD, see LICENSE for more details.
"""
from __future__ import print_function

# Standard library
import sys
import os
import re
import time
from getopt import gnu_getopt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
try:
    import subprocess32 as subprocess
except ImportError:
    # Standard library
    import subprocess


class WhenChanged(FileSystemEventHandler):
    # files to exclude from being watched
    exclude = re.compile(r'|'.join(r'(.+/)?'+ a for a in [
        # Vim swap files
        r'\..*\.sw[px]*$',
        # file creation test file 4913
        r'4913$',
        # backup files
        r'.~$',
        # git directories
        r'\.git/?',
        # __pycache__ directories
        r'__pycache__/?',
        ]))

    def __init__(self, files, command, recursive=False, run_once=False, run_at_start=False):
        self.files = files
        paths = {}
        for f in files:
            paths[os.path.realpath(f)] = f
        self.paths = paths
        self.command = command
        self.recursive = recursive
        self.run_once = run_once
        self.run_at_start = run_at_start
        self.last_run = 0

        self.observer = Observer(timeout=0.1)

        for p in self.paths:
            if os.path.isdir(p):
                # Add directory
                self.observer.schedule(self, p, recursive=True)
            else:
                # Add parent directory
                p = os.path.dirname(p)
                self.observer.schedule(self, p)


    def run_command(self, thefile):
        if self.run_once:
            if os.path.exists(thefile) and os.path.getmtime(thefile) < self.last_run:
                return
        new_command = []
        for item in self.command:
            new_command.append(item.replace('%f', thefile))
        subprocess.call(new_command, shell=(len(new_command) == 1))
        self.last_run = time.time()

    def is_interested(self, path):
        if self.exclude.match(path):
            return False

        if path in self.paths:
            return True

        path = os.path.dirname(path)
        if path in self.paths:
            return True

        if self.recursive:
            while os.path.dirname(path) != path:
                path = os.path.dirname(path)
                if path in self.paths:
                    return True

        return False

    def on_change(self, path):
        if self.is_interested(path):
            self.run_command(path)

    def on_created(self, event):
        if self.observer.__class__.__name__ == 'InotifyObserver':
            # inotify also generates modified events for created files
            return

        if not event.is_directory:
            self.on_change(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.on_change(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.on_change(event.dest_path)

    def run(self):
        if self.run_at_start:
            self.run_command('/dev/null')

        self.observer.start()
        try:
            while True:
                time.sleep(60 * 60)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()


def print_usage(prog):
    print(__doc__ % {'prog': prog}, end='')

def parse_args(argv):
    """
    Parse the various args and returns a WhenChanged object.

    The function can return None if the arguments were correct but
    could not build an object (eg display help).

    The function raises ValueError in case of bad arguments.
    """
    files = []
    command = []
    recursive = False
    verbose = False
    run_once = False
    run_at_start = False

    prog = os.path.basename(argv.pop(0))
    args, shiftargs = gnu_getopt(argv, 'hvr1sc:', longopts=["help"])
    for arg,argopt in args:
        if arg == '-h' or arg == '--help':
            print_usage(prog)
            return None
        elif arg == '-v':
            verbose = True
        elif arg == '-r':
            recursive = True
        elif arg == '-1':
            run_once = True
        elif arg == '-s':
            run_at_start = True
        elif arg == '-c':
            # special case: all following arguments are part of a command
            r_c = re.compile(r'\-[^\-]*c(.*)')
            a = [a for a in argv if r_c.match(a)][0]
            a_i = argv.index(a)

            # two things to take as argument to -c: directly attached and following: -carg1 arg2
            remain = r_c.match(a).groups()[0]
            command = []
            if remain != '':
                command += [remain]
            if a_i < len(argv):
                command += argv[a_i + 1:]
            
            # shiftargs ignores any option before -c and any argument after -c
            shiftargs = [a for a in argv[0:a_i] if not re.match(r'\-', a) ]
            break
        else:
            break

    if command and not shiftargs or not command and len(shiftargs) < 2:
        raise ValueError()

    if command:
        files = shiftargs
    else:
        files = [shiftargs[0]]
        command = shiftargs[1:]

    print_command = ' '.join(command)

    # Tell the user what we're doing
    if len(files) > 1:
        l = ["'%s'" % f for f in files]
        s = ', '.join(l[:-1]) + ' or ' + l[-1]
        if verbose:
            print("When %s changes, run '%s'" % (s, print_command))
    else:
        if verbose:
            print("When '%s' changes, run '%s'" % (files[0], print_command))

    return WhenChanged(files, command, recursive, run_once, run_at_start)

def main():
    try:
        wc = parse_args(sys.argv)
    except ValueError:
        print_usage(prog)
        exit(2)

    if wc is None:
        exit(0)

    try:
        wc.run()
    except KeyboardInterrupt:
        print()
        exit(0)

#!/usr/bin/env python
"""%(prog)s - run a command when a file is changed

Usage: %(prog)s [-vr1s] FILE COMMAND...
       %(prog)s [-vr1s] FILE [FILE ...] -c COMMAND

FILE can be a directory. Use %%f to pass the filename to the command.

Options:
-r Watch recursively
-v Verbose output
-1 Don't re-run command if files changed while command was running
-s Run command immediately at start

Copyright (c) 2011-2016, Johannes H. Jensen.
License: BSD, see LICENSE for more details.
"""
from __future__ import print_function

# Standard library
import sys
import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
try:
    import subprocess32 as subprocess
except ImportError:
    # Standard library
    import subprocess


class WhenChanged(FileSystemEventHandler):
    # Exclude Vim swap files, its file creation test file 4913 and backup files
    exclude = re.compile(r'^\..*\.sw[px]*$|^4913$|.~$')

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
        basename = os.path.basename(path)

        if self.exclude.match(basename):
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


def main():
    args = sys.argv
    prog = os.path.basename(args.pop(0))

    if '-h' in args or '--help' in args:
        print_usage(prog)
        exit(0)

    files = []
    command = []
    recursive = False
    verbose = False
    run_once = False
    run_at_start = False

    while args and args[0][0] == '-':
        flag = args.pop(0)
        if flag == '-v':
            verbose = True
        elif flag == '-r':
            recursive = True
        elif flag == '-1':
            run_once = True
        elif flag == '-s':
            run_at_start = True
        elif flag == '-c':
            command = args
            args = []
        else:
            break

    if '-c' in args:
        cpos = args.index('-c')
        files = args[:cpos]
        command = args[cpos + 1:]
    elif len(args) >= 2:
        files = [args[0]]
        command = args[1:]

    if not files or not command:
        print_usage(prog)
        exit(1)

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

    wc = WhenChanged(files, command, recursive, run_once, run_at_start)

    try:
        wc.run()
    except KeyboardInterrupt:
        print()
        exit(0)

#!/usr/bin/env python
"""%(prog)s - run a command when a file is changed

Usage: %(prog)s [-v] [-r] [-1] [-s] FILE COMMAND...
       %(prog)s [-v] [-r] [-1] [-s] FILE [FILE ...] -c COMMAND

FILE can be a directory. Watch recursively with -r.
Verbose output with -v.
-1 (run once) to not rerun if changes occured while the command was running.
-s (run at start) to run the command immediately at start.
Use %%f to pass the filename to the command.

Copyright (c) 2011, Johannes H. Jensen.
License: BSD, see LICENSE for more details.
"""
from __future__ import print_function

# Standard library
import sys
import os
import re
import time
import pyinotify
try:
    import subprocess32 as subprocess
except ImportError:
    # Standard library
    import subprocess


class WhenChanged(pyinotify.ProcessEvent):
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

    def process_IN_CLOSE_WRITE(self, event):
        self.on_change(event.pathname)

    def process_IN_MOVED_TO(self, event):
        self.on_change(event.pathname)

    def run(self):
        if self.run_at_start:
            self.run_command('/dev/null')

        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, self)

        # Add watches (IN_CREATE is required for auto_add)
        mask = (pyinotify.IN_CLOSE_WRITE |
                pyinotify.IN_MOVED_TO |
                pyinotify.IN_CREATE)

        for p in self.paths:
            if os.path.isdir(p):
                # Add directory
                wdd = wm.add_watch(p, mask, rec=self.recursive,
                                   auto_add=self.recursive)
            else:
                # Add parent directory
                path = os.path.dirname(p)
                wdd = wm.add_watch(path, mask)

        notifier.loop()


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

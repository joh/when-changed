#!/usr/bin/env python
"""%(prog)s - run a command when a file is changed

Usage: %(prog)s [-r] FILE COMMAND...
       %(prog)s [-r] FILE [FILE ...] -c COMMAND

FILE can be a directory. Watch recursively with -r.
Use %%f to pass the filename to the command.

Copyright (c) 2011, Johannes H. Jensen.
License: BSD, see LICENSE for more details.
"""
from __future__ import print_function

import sys
import os
import re
import pyinotify


class WhenChanged(pyinotify.ProcessEvent):
    # Exclude Vim swap files, its file creation test file 4913 and backup files
    exclude = re.compile(r'^\..*\.sw[px]*$|^4913$|.~$')

    def __init__(self, files, command, recursive=False):
        self.files = files
        self.paths = {os.path.realpath(f): f for f in files}
        self.command = command
        self.recursive = recursive

    def run_command(self, file):
        os.system(self.command.replace('%f', file))

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

    def process_IN_CLOSE_WRITE(self, event):
        path = event.pathname
        if self.is_interested(path):
            self.run_command(path)

    def run(self):
        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, self)

        # Add watches (IN_CREATE is required for auto_add)
        mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE
        watched = set()
        for p in self.paths:
            if os.path.isdir(p) and not p in watched:
                # Add directory
                wdd = wm.add_watch(p, mask, rec=self.recursive,
                                   auto_add=self.recursive)
            else:
                # Add parent directory
                path = os.path.dirname(p)
                if not path in watched:
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

    if args and args[0] == '-r':
        recursive = True
        args.pop(0)

    if '-c' in args:
        cpos = args.index('-c')
        files = args[:cpos]
        command = args[cpos+1:]
    elif len(args) >= 2:
        files = [args[0]]
        command = args[1:]

    if not files or not command:
        print_usage(prog)
        exit(1)

    command = ' '.join(command)

    # Tell the user what we're doing
    if len(files) > 1:
        l = ["'%s'" % f for f in files]
        s = ', '.join(l[:-1]) + ' or ' + l[-1]
        print("When %s changes, run '%s'" % (s, command))
    else:
        print("When '%s' changes, run '%s'" % (files[0], command))

    wc = WhenChanged(files, command, recursive)
    try:
        wc.run()
    except KeyboardInterrupt:
        print()
        exit(0)

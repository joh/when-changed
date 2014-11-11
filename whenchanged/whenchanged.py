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

# Standard library
import sys
import os
import re
from datetime import datetime

# External modules.
import pyinotify
try:
    import subprocess32 as subprocess
except ImportError:
    # Standard library
    import subprocess


def run_once(fn):
    '''
    When event trigger interval less than 0.5s, treat
    as one trigger
    '''
    def wrapper(self, event):
        now = datetime.now()
        delta = now - self.last_run_time
        # Some tmp files will trigger event, use pathname to exclude them.
        if self.last_path != event.pathname or delta.total_seconds() > 0.5:
            fn(self, event)
            self.last_run_time = now
            self.last_path = event.pathname
    return wrapper


class WhenChanged(pyinotify.ProcessEvent):
    # Exclude Vim swap files, its file creation test file 4913 and backup files
    exclude = re.compile(r'^\..*\.sw[px]*$|^4913$|.~$')

    def __init__(self, files, command, recursive=False, suffixes=None):
        self.files = files
        paths = {}
        for f in files:
            paths[os.path.realpath(f)] = f
        self.paths = paths
        self.command = command
        self.recursive = recursive
        self.suffixes = suffixes.split(',') if suffixes else []
        self.last_run_time = datetime.now()
        self.last_path = ''

    def run_command(self, thefile):
        new_command = []
        for item in self.command:
            if item == "%f":
                item = thefile
            new_command.append(item)
        subprocess.call(new_command)

    def is_interested(self, path):
        basename = os.path.basename(path)
        suffix = path.split('.')[-1] if os.path.isfile(path) else None
        is_allowed = suffix in self.suffixes

        if self.exclude.match(basename):
            return False

        if path in self.paths:
            return True

        path = os.path.dirname(path)
        if path in self.paths:
            return True if is_allowed else False

        if self.recursive:
            while os.path.dirname(path) != path:
                path = os.path.dirname(path)
                if path in self.paths:
                    return True if is_allowed else False
        return False

    def on_change(self, path):
        if self.is_interested(path):
            self.run_command(path)

    @run_once
    def process_IN_CLOSE_WRITE(self, event):
        self.on_change(event.pathname)

    @run_once
    def process_IN_MOVED_TO(self, event):
        self.on_change(event.pathname)

    def run(self):
        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, self)

        # Add watches (IN_CREATE is required for auto_add)
        mask = (pyinotify.IN_CLOSE_WRITE |
                pyinotify.IN_MOVED_TO |
                pyinotify.IN_CREATE)

        watched = set()
        for p in self.paths:
            if os.path.isdir(p) and p not in watched:
                # Add directory
                wm.add_watch(p, mask, rec=self.recursive,
                             auto_add=self.recursive)
            else:
                # Add parent directory
                path = os.path.dirname(p)
                if path not in watched:
                    wm.add_watch(path, mask)

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

    # Suffixes e.g. 'py,js,css' do not use space after comma
    # Special usage: when-changed -r path/ -s py,js -c COMMAND
    suffixes = None
    if '-s' in args:
        spos = args.index('-s')
        suffixes = args[spos+1]
        # Below order can not be changed
        args.pop(spos+1)
        args.pop(spos)
    suffix_info = ' all [%s] files' % suffixes if suffixes else ''

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

    print_command = ' '.join(command)

    # Tell the user what we're doing
    fileinfo = ''
    if len(files) > 1:
        l = ["'%s'" % f for f in files]
        fileinfo = ', '.join(l[:-1]) + ' or ' + l[-1]
        fileinfo += suffix_info
    else:
        # one file or one directory
        fileinfo = files[0] + suffix_info
    print("When '%s' changes, run '%s'" % (fileinfo, print_command))

    wc = WhenChanged(files, command, recursive, suffixes)
    try:
        wc.run()
    except KeyboardInterrupt:
        print()
        exit(0)


if __name__ == '__main__':
    main()

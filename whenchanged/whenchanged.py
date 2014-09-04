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

# External modules.
import pyinotify
try:
    import subprocess32 as subprocess
except ImportError:
    # Standard library
    import subprocess


class WhenChanged(pyinotify.ProcessEvent):
    # Exclude Vim swap files, its file creation test file 4913 and backup files
    exclude = re.compile(r'^\..*\.sw[px]*$|^4913$|.~$')

    def __init__(self, files, command, recursive=False, mods_only=False, renames_only=False):
        self.files = files
        paths = {}
        for f in files:
            paths[os.path.realpath(f)] = f
        self.paths = paths
        self.command = command
        self.recursive = recursive
        self.mods_only = mods_only
        self.renames_only = renames_only

    def run_command(self, thefile):
        command = self.command
        if command is None or len(command) == 0:
            print(thefile)
            return

        new_command = []
        for item in self.command:
            if item == "%f":
                item = thefile
            new_command.append(item)
        subprocess.call(new_command)

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
        if not self.renames_only:
            self.on_change(event.pathname)

    def process_IN_MOVED_TO(self, event):
        if not self.mods_only:
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

class OldArgs(object):
    mods_only = False
    renames_only = False

    def __init__(self, files, command, recursive):
        self.files = files
        self.command = command
        self.recursive = recursive

def old_parse_args():
    """
    """
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

    return OldArgs(files, command, recursive)


def main():
    try:
        import argparse
    except ImportError:
        args = old_parse_args()
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument(
                "-r",
                '--recursive',  
                help="Recurse into directories.",
                action='store_true')
        mutex = parser.add_mutually_exclusive_group()
        mutex.add_argument(
                '--renames-only',  
                help="Only respond to renames; not file modifications.",
                action='store_true')
        mutex.add_argument(
                '--mods-only',  
                help="Only respond to file modifications.",
                action='store_true')
        parser.add_argument(
                "files",
                help="The files or folders to watch.",
                action='store',
                nargs='+')
        parser.add_argument(
                "-c",
                '--command',  
                help="The command (and optionally arguments) to execute.",
                action='store',
                nargs=argparse.REMAINDER,
                metavar='ARG')
        args = parser.parse_args() 

    command = args.command
    files = args.files
    if command is not None and len(command) > 0:
        print_command = ' '.join(command)
    else:
        print_command = "<print the file>"

    # Tell the user what we're doing
    if len(files) > 1:
        l = ["'%s'" % f for f in files]
        s = ', '.join(l[:-1]) + ' or ' + l[-1]
        print("When %s changes, run '%s'" % (s, print_command))
    else:
        print("When '%s' changes, run '%s'" % (files[0], print_command))

    wc = WhenChanged(**vars(args))
    try:
        wc.run()
    except KeyboardInterrupt:
        print()
        exit(0)


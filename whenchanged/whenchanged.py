#!/usr/bin/env python
"""
when-changed - run a command when a file is changed

Usage: when-changed FILE COMMAND...
       when-changed FILE [FILE ...] -c COMMAND

Copyright (c) 2011, Johannes H. Jensen.
License: BSD, see LICENSE for more details.
"""
import sys
import os
import re
import pyinotify

usage =  'Usage: %(prog)s FILE COMMAND...'
usage += '\n       %(prog)s FILE [FILE ...] -c COMMAND...'
description = 'Run a command when a file is changed.\n'
description += 'Use %f to pass the filename to the command.\n'

def print_usage(prog):
    print usage % {'prog': prog}

def print_help(prog):
    print_usage(prog)
    print "\n" + description

class WhenChanged(pyinotify.ProcessEvent):
    # Exclude Vim swap files, its file creation test file 4913 and backup files
    exclude = re.compile(r'^\..*\.sw[px]*$|^4913$|.~$')

    def __init__(self, files, command, exclude=None, verbose=False):
        self.files = files
        self.paths = {os.path.realpath(f): f for f in files}
        self.command = command
        self.verbose = verbose

    def run_command(self, file):
        os.system(self.command.replace('%f', file))

    def is_interested(self, path):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        if self.exclude.match(basename):
            return False

        return path in self.paths or dirname in self.paths

    def process_IN_CLOSE_WRITE(self, event):
        path = event.pathname
        if self.is_interested(path):
            print path, "changed!"
            self.run_command(path)

    def run(self):
        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, self)

        # Add watches
        mask = pyinotify.IN_CLOSE_WRITE
        # TODO: Avoid duplicates
        watched = set()
        for p in self.paths:
            if os.path.isdir(p) and p not in watched:
                # Add directory
                print "Watch directory", p
                wdd = wm.add_watch(p, mask, rec=True, auto_add=True)
            else:
                # Add parent directory
                path = os.path.dirname(p)
                if not path in watched:
                    print "Watch directory", path, "to monitor", p
                    wdd = wm.add_watch(path, mask)

            print wdd

        notifier.loop()


def main():
    args = sys.argv
    prog = args.pop(0)

    if '-h' in args or '--help' in args:
        print_help(prog)
        exit(0)

    files = []
    command = []

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
        print "When %s changes, run '%s'" % (s, command)
    else:
        print "When '%s' changes, run '%s'" % (files[0], command)

    wc = WhenChanged(files, command, True)
    try:
        wc.run()
    except KeyboardInterrupt:
        print
        exit(0)

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
import time

usage =  'Usage: %(prog)s FILE COMMAND...'
usage += '\n       %(prog)s FILE [FILE ...] -c COMMAND...'
description = 'Run a command when a file is changed.\n'
description += 'You can pass filename to the command\n'
description += 'by "%f" variable.'

def print_usage(prog):
    print usage % {'prog': prog}

def print_help(prog):
    print_usage(prog)
    print "\n" + description


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

    # Store initial mtimes
    try:
        mtimes = [os.stat(f).st_mtime for f in files]
    except OSError as e:
        print e
        exit(1)

    # Tell the user what we're doing
    if len(files) > 1:
        l = ["'%s'" % f for f in files]
        s = ', '.join(l[:-1]) + ' or ' + l[-1]
        print "When %s changes, run '%s'" % (s, command)
    else:
        print "When '%s' changes, run '%s'" % (files[0], command)

    # Start polling for changes
    try:
        while True:
            for i, f in enumerate(files):
                try:
                    t = os.stat(f).st_mtime
                    if t != mtimes[i]:
                        mtimes[i] = t
                        os.system(command.replace('%f', f))

                except OSError as e:
                    # Some editors (like vim) will first write to a temporary
                    # file, then delete the original file before renaming the
                    # temporary file back to the original filename.
                    # Thus the original file might not exist at the moment
                    # we do os.stat() so we ignore any errors here.
                    pass

            time.sleep(0.5)
    except KeyboardInterrupt:
        print ""
        exit(0)

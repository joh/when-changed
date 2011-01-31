#!/usr/bin/env python
"""
when-changed - run a command when a file is changed

Usage: when-changed FILE COMMAND...
"""
import sys
import os
import time

usage = 'Usage: %(prog)s FILE COMMAND...'
description = 'Run a command when a file is changed'

def print_usage(prog):
    print usage % {'prog': prog}

def print_help(prog):
    print_usage(prog)
    print "\n" + description


if __name__ == '__main__':
    prog = sys.argv[0]
    
    if sys.argv[1] in ('-h', '--help'):
        print_help(prog)
        exit(0)
    
    if len(sys.argv) < 3:
        print_usage(prog)
        exit(1)
    
    filename = sys.argv[1]
    command = ' '.join(sys.argv[2:])
    
    # Store initial mtime
    try:
        mtime = os.stat(filename).st_mtime
    except OSError as e:
        print e
        exit(1)
    
    # Start polling for changes
    while True:
        try:
            t = os.stat(filename).st_mtime
            if t != mtime:
                mtime = t
                os.system(command)
            
        except OSError as e:
            print e.strerror
            # TODO: Exit here?
        
        time.sleep(0.5)


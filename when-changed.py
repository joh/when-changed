#!/usr/bin/env python
"""
when-changed - run a command when a file is changed

Usage: when-changed FILE COMMAND...
       when-changed FILE [FILE ...] -c COMMAND
"""
import sys
import os
import time

usage =  'Usage: %(prog)s FILE COMMAND...'
usage += '\n       %(prog)s FILE [FILE ...] -c COMMAND...'
description = 'Run a command when a file is changed'

def print_usage(prog):
    print usage % {'prog': prog}

def print_help(prog):
    print_usage(prog)
    print "\n" + description


if __name__ == '__main__':
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
    else:
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
    
    # Start polling for changes
    while True:
        for i, f in enumerate(files):
            try:
                t = os.stat(f).st_mtime
                if t != mtimes[i]:
                    mtimes[i] = t
                    os.system(command)
                
            except OSError as e:
                print e.strerror
                # TODO: Exit here?
        
        time.sleep(0.5)


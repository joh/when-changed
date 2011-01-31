#!/usr/bin/env python
"""
when-changed - execute a command when a file is changed
"""
import sys
import os
import time

if __name__ == '__main__':
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='execute a command when a file is changed'
    )
    
    parser.add_argument('filename', help='file to watch for changes')
    parser.add_argument('command', nargs='+',
        help='command to execute when file is changed')
    
    args = parser.parse_args()
    filename = args.filename
    command = ' '.join(args.command)
    
    #print filename
    #print command
    
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
                print filename, "changed"
            
        except OSError as e:
            print e.strerror
            # TODO: Exit here?
        
        time.sleep(0.5)


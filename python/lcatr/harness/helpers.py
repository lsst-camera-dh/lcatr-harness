#!/usr/bin/env python
'''
This module provides helpful things for producer and validator
processes, if they be written in Python.

Note, module is not used by the rest of the harness.
'''

import os
from glob import glob

def dependency_glob(pattern, jobname = None, paths = None):
    '''
    Return list of paths to the files matching glob <pattern> or None.

    If the job name <jobname> is given only consider files in its
    output area, otherwise only consider file in the output area where
    the first match is made.  If a list of output <paths> to consider
    are not given then the value of the environment variable
    LCATR_DEPENDENCY_PATH is used.
    '''

    if not paths:
        paths = os.environ.get('LCATR_DEPENDENCY_PATH')
    if not paths: return
    if isinstance(paths, basestring): 
        paths = paths.split(':')
        
    ret = list()
    for path in paths:
        if jobname and not '/'+jobname+'/' in path: # kind of a cheat
            continue
        hit = glob(os.path.join(path,pattern))
        if hit:
            ret += hit
        continue
    return ret

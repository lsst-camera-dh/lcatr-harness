#!/usr/bin/env python
'''
This module provides helpful things for producer and validator
processes, if they be written in Python.

Note, module is not used by the rest of the harness.
'''
#from past.builtins import basestring

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

    if isinstance(paths, str):
        paths = paths.split(':')
    else:
        try:
            if isintance(paths, unicode):
                paths = paths.split(':')
        except NameError:
            pass

    #if isinstance(paths, (str,unicode)): 
    #    paths = paths.split(':')
        
    ret = list()
    for path in paths:
        if jobname and not '/'+jobname+'/' in path: # kind of a cheat
            continue
        hit = glob(os.path.join(path,pattern))
        if hit:
            ret += hit
        continue
    return ret

def dependency_jobids( ):
    '''
    Return a dict mapping jobname to job id for all prerequisite jobs
    '''

    paths = os.environ.get('LCATR_DEPENDENCY_PATH')
    if not paths: return

    # We need to assume formation of paths by JH does not change.  Relative to stage directory
    # that's (in eTraveler terminology)
    #    hardwareTypeName/lsstId/jobName/jobVersion/activityId
    #if isinstance(paths, (str, unicode)):
    if isinstance(paths, str):
        paths = paths.split(':')
    else:
        try:
            if isintance(paths, unicode):
                paths = paths.split(':')
        except NameError:
            pass

    d = {}
    for path in paths:
        cmps = path.split('/')
        last = len(cmps) - 1
        d[cmps[last-2]] = cmps[last]
    return d

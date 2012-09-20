#!/usr/bin/env python
'''
Handle environment.
'''

import os

def module_name(test_name, test_version = ""):
    '''
    Build module name.

    This defines the expected construction of environment module names.
    '''
    return '-'.join(test_name, test_version)

def module_environment(name, version = "", env = None):
    '''
    Return a dictionary of environment variables set by the given
    module name and version.

    If env is given it is assumed to hold the initial environment.  It
    not specified the current process environment is used.
    '''
    ret = {}
    if not env: 
        env = {}
        env.update(os.environ)
        pass
    
    
    
    

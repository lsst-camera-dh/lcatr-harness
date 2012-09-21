#!/usr/bin/env python
'''
Test the lcatr.harness.config module
'''

import os
from lcatr.harness import config

def test_dump():
    cfgfile = os.path.join(os.path.dirname(__file__), 'lcatr.cfg')
    c = config.Config(name="test_config", site='TESTSITE', filename = cfgfile)
    for k,v in sorted(c.__dict__.iteritems()):
        if k[0] == '_': continue
        print '\t%s = %s' % (k,v)


def test_incomplete():
    '''
    Make an incomplete config object
    '''

    c = config.Config(name="test_config")
    assert not c.complete(), 'Incomplete config object says it is complete'
    

def test_complete():
    '''
    Make a complete config object
    '''    
    c = config.Config("test_config","v0.0")
    for req in c.required_parameters:
        if req in ['name','version']: continue
        c.set(req,"foo")
    assert c.complete(), 'Complete config object says it is not'
    assert str(c) == 'Config: "test_config" (v0.0)'

if __name__ == '__main__':
    
    test_dump()
    test_incomplete()
    test_complete()

#!/usr/bin/env python
'''
Test the lcatr.harness.config module
'''

from lcatr.harness import config

def test_incomplete():
    '''
    Make an incomplete config object
    '''

    c = config.Config(name="test_config",version="v0.0")
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
    
    test_incomplete()
    test_complete()

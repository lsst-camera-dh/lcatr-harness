#!/usr/bin/env python
'''
Test the lcatr.harness.environment module
'''

from lcatr.harness import environment

em = None

def test_create():
    'Test creating interface to modules.sf.net'

    global em
    em = environment.Modules()
    return

def test_load():
    'Test loading the "dot" module'
    em.load('dot')
    assert 'dot' in em.env['LOADEDMODULES'], 'The "dot" module not loaded'
    return

def test_unload():
    'Test unloading the "dot" module'
    em.unload('dot')
    assert 'LOADEDMODULES' not in em.env.keys(), 'Some modules still loaded'
    return

def test_dump():

    for k,v in em.env.iteritems():
        print '%s = %s' % (k,v)
        continue
    return

if __name__ == '__main__':
    test_create()
    test_load()
    test_unload()
    #test_dump()

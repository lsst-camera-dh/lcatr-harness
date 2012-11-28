#!/usr/bin/env python
'''
Test the lcatr.harness.environment module
'''

from lcatr.harness import environment

em = None

def test_guess_modules_path():
    'Test guessing the modules path'
    print environment.guess_modules_path()

def test_create():
    'Test creating interface to modules.sf.net'

    global em
    em = environment.Modules()
    em.guess_setup()
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
        if 'MOD' not in k: continue
        print '%s = %s' % (k,v)
        continue
    return


def do_all():
    test_guess_modules_path()
    test_create()
    test_load()
    test_unload()
    test_dump()

if __name__ == '__main__':
    do_all()

#!/usr/bin/env python
'''
Run some or all of the tests.
'''

import sys, os
import re
from glob import glob

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0,base + '/python')

def get_test_names():
    ret = []
    for testpy in glob(base + '/tests/test_*.py'):
        found = re.search('test_(.*)\.py', testpy)
        if not found:
            continue
        ret.append(found.group(1))
        continue
    return ret

def do_test(name):
    modname = 'test_%s' % name
    exec 'import %s' % modname
    mod = eval(modname)
    for what in dir(mod):
        if not what.startswith('test_'): 
            continue
        print 'Testing: %s:%s' % (name, what)
        meth = eval('mod.%s' % what)
        meth()
        continue
    

if '__main__' == __name__:
    tnames = sys.argv[1:]
    if not tnames:
        tnames = get_test_names()

    for tname in tnames:
        do_test(tname)

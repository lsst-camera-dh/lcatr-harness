#!/usr/bin/env python
'''
test lcatr.harness.main
'''

import os
from lcatr.harness import main

def test_cmdline():
    here = os.path.dirname(os.path.realpath(__file__))
    cfgfile = here + '/lcatr.cfg'
    main.cmdline(['--config', cfgfile,
                  '--context','UNITTEST',
                  '--unit-id','4-1201',
                  '--job-id','0',   # fixme: need to reslolve externally
                  '--job', 'fake']) # version resolved in config file


if '__main__' == __name__:
    test_cmdline()

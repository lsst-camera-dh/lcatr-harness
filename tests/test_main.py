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
                  '--job-id','0', # note: this is normally given by LIMS
                  '--job', 'fake', # version resolved in config file
                  '--archive-root', '/tmp',
                  '--lims-url','http://localhost/',
                  '--archive-user','archive',
                  ])

if '__main__' == __name__:
    test_cmdline()

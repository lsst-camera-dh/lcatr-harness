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
                  'configure'])

if '__main__' == __name__:
    test_cmdline()

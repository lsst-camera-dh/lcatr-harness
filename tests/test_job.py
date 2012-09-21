#!/usr/bin/env python
'''
Test the lcatr.harness.job module.
'''

import os
from lcatr.harness import job, config

jerb = None

def test_create():
    global job
    cfgfile = os.path.join(os.path.dirname(__file__), 'lcatr.cfg')
    cfg = config.Config(name='test_config', site='TESTSITE', filename=cfgfile)
    cfg.ccd_id = 0
    cfg.job_id = 0

    jerb = job.Job(cfg)
    print 'Dey tuek er jerbs:',jerb
    return

if __name__ == '__main__':
    test_create()

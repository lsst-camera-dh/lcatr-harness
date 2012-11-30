#!/usr/bin/env python
'''
Test the lcatr.harness.job module.  This should be run through fakerunner
'''

import os
from lcatr.harness import job, config

from test_config import make_cfgfile

jerb = None

def test_create():
    global jerb

    fd, fn = make_cfgfile()
    cfg = config.Config(filename=fn, local='LTEST')
    cfg.ccd_id = 0
    cfg.job_id = 0              # note, this is normally given to us by LIMS
    cfg.job = 'fake'
    cfg.version = 'v0'
    cfg.unit_id = '000000'

    jerb = job.Job(cfg)
    #print 'Dey tue ker jerbs:',jerb
    #print '\n'.join(['\t%s = %s' % (k,v) for k,v in jerb.env.iteritems()])
    return

def test_archive_exists():
    assert not jerb.archive_exists(), 'Archive directory exists but we did not make one'
    return

if __name__ == '__main__':
    test_create()
    test_archive_exists()

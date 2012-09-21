#!/usr/bin/env python
'''
Test the lcatr.harness.job module.
'''

import os
from lcatr.harness import job, config

jerb = None

def test_create():
    global jerb
    cfgfile = os.path.join(os.path.dirname(__file__), 'lcatr.cfg')
    cfg = config.Config(name='test_config', site='TESTSITE', filename=cfgfile)
    cfg.ccd_id = 0
    cfg.job_id = 0

    jerb = job.Job(cfg)
    #print 'Dey tuek er jerbs:',jerb
    #print '\n'.join(['\t%s = %s' % (k,v) for k,v in jerb.env.iteritems()])
    return

def test_archive_not_there():
    there = jerb.archive_exists()
    assert not there, 'Archive exists at %s' % jerb.cfg.archive_rsync_path()
    print 'Not there:',jerb.cfg.subdir('archive')

if __name__ == '__main__':
    test_create()
    test_archive_not_there()

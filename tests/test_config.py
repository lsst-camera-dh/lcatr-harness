#!/usr/bin/env python
'''
Test the lcatr.harness.config module
'''

import os
from lcatr.harness import config
import tempfile

cfgfd = None,
cfgfile = None

def make_cfgfile():
    fd = tempfile.NamedTemporaryFile()
    fn = fd.name

    fd.write('''
[DEFAULT]
unit_type = CCD
unknown_parameter = 42

[local LTEST]
local_root = /tmp
site = TESTSITE

[site TESTSITE]
archive_root = /tmp
archive_user = testuser
archive_host = testhost

[job fake]
version = v0
''')
    fd.flush()
    #fd.close() # <-- don't do it
    return fd, fn

def test_make_cfgfile():
    global cfgfd
    global cfgfile 
    cfgfd, cfgfile = make_cfgfile()
    return 

def dump(msg,c):
    print msg
    for k,v in sorted(c.__dict__.iteritems()):
        if k[0] == '_': continue
        print '\t%s = %s' % (k,v)
        continue
    return

def test_env():
    os.environ['LCATR_SITE'] = 'TESTSITE'
    c = config.Config(config=cfgfile)
    assert c.site == 'TESTSITE'
    #dump('After env',c)
    return

def test_dump():
    c = config.Config(config = cfgfile)
    assert c.unit_type == 'CCD'
    assert c.archive_user == 'testuser'
    #dump('Dump',c)
    return

def test_incomplete():
    '''
    Make an incomplete config object
    '''
    c = config.Config(filename=cfgfile)
    assert not c.complete(), 'Incomplete config object says it is complete'
    
def test_missing():
    c = config.Config(filename=cfgfile)
    missing = set(c.missing())
    missed = set(['context', 'version', 'job_id', 'localjob', 'unit_id'])
    assert missing == missed, "Unexpected missing: %s != %s" % (missing,missed)

    e1 = set(c.extra())
    e2 = set(['unknown_parameter'])
    assert e1 == e2, "Unexpected extra: %s != %s" %(e1,e2)
    return

if __name__ == '__main__':
    test_make_cfgfile()
    test_env()
    test_dump()
    test_incomplete()
    test_missing()


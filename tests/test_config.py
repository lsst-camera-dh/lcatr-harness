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
    #print c.missing()
    #print c.extra()
    assert c.missing() == [
        'job_id', 'stamp', 'stage_root', 'unit_id', 'localjob', 
        'modules_version', 'version', 'context', 'operator', 
        'modules_home', 'modules_cmd', 'modules_path'
        ]
    assert c.extra() == ['unknown_parameter']
    return

if __name__ == '__main__':
    test_make_cfgfile()
    test_env()
    test_dump()
    test_incomplete()
    test_missing()


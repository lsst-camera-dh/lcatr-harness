#!/usr/bin/env python

import os

from lcatr.harness import remote

remotehost = "rftpexp02.rhic.bnl.gov"

def test_rhostname():
    #lname = os.uname()[1]
    lname = remotehost
    s,o,e = remote.cmd("hostname", remotehost)
    assert s == 0, 'Got non-zero status for hostname: %d, %s' % (s,e)
    rname = o.strip()
    assert lname == rname, \
        'Did not get expected hostname "%s" != "%s"' % (lname,rname)
    return

def try_rstat(path,expect_success):
    try:
        s,o,e = remote.stat(path,host='doesnotexist')
    except RuntimeError,msg:
        #print 'Error as expected: "%s"' % msg
        pass
    else:
        raise

    s,o,e = remote.stat(path, host=remotehost)
    if not expect_success and s == 0:
        assert False, 'Expected failure but got (%d) with remote stat %s' % \
            (s,path)

    if expect_success and s != 0:
        assert False, 'Expected success but got (%d) with remote stat %s' % \
            (s,path)

    out = o.strip()

    if expect_success and not out:
        assert False, 'Expected success but not output for %s' % path
    if not expect_success and out:
        assert False, 'Expected failure got output for %s' % path
    return

def test_rstat_failure():
    try_rstat('/does-not-exist', False)
    return
def test_rstat_success():
    try_rstat('/tmp', True)
    return
    

def test_rsync():
    import tempfile
    here = os.path.realpath(os.path.dirname(__file__))
    src = 'localhost:' + here
    dst = tempfile.mkdtemp()
    remote.rsync(src,dst)
    print '%s --> %s' % (src, dst)
    return

if __name__ == '__main__':
    
    test_rhostname()
    test_rstat_success()
    #test_rstat_failure()
    #test_rsync()

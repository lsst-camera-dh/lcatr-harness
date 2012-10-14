#!/usr/bin/env python
'''
Test the commands module
'''

from lcatr.harness import commands
from lcatr.harness.util import log, DEBUG

log.setLevel(DEBUG)

def test_succeed():

    commands.execute("ls -l /tmp", out = log.debug)

    return


def test_fail():

    cmdstr = "/bin/doesnotexist"

    try:
        commands.execute(cmdstr, out = log.debug)
    except OSError, err:
        print 'Caught OSError as expected'
    else:
        assert 'Should have failed with cmd: "%s"' % cmdstr

    return

def test_false():

    cmdstr = "/bin/false"

    try:
        commands.execute(cmdstr, out = log.debug)
    except commands.CommandFailure, err:
        print 'Caught CommandFailure,"%s" as expected' % err
    else:
        assert 'Should have failed with cmd: "%s"' % cmdstr

    return

if '__main__' == __name__:
    test_succeed()
    test_fail()
    test_false()


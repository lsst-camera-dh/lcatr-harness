#!/usr/bin/env python
'''
Test the lcatr.harness.util module
'''

from lcatr.harness import util

import tempfile

basedir = tempfile.mkdtemp()

def test_file_logger():
    
    name = 'test_file_logger'
    filename = '%s/%s.log' % (basedir, name)
    print 'logging to: %s' % filename
    l = util.file_logger(name,filename)
    l.debug('This is a debug msg')
    l.info('This is an info msg')
    l.warning('This is a warning msg')


if '__main__' == __name__:
    test_file_logger()

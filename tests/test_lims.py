#!/usr/bin/env python
'''
test lcatr.harness.lims
'''
from lcatr.harness import lims

cfg = {
    'operator':'testuser',
    'job':'testjob',
    'version':'v0',
    }

def test_url():
    print lims.make_url('http://lims.example.com/', 'register',**cfg)

if '__main__' == __name__:
    test_url()

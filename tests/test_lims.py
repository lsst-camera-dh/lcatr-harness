#!/usr/bin/env python
'''
Test the (real) LIMS web service
'''

lims_url = 'https://www.lsst.bnl.gov:8088/'

import time
from lcatr.harness import lims

from lcatr.harness.job import Job

a_job_id = None

def test_register():
    res = lims.register(lims_url=lims_url,
                        stamp=time.time(),
                        unit_type = 'CCD',
                        unit_id = '100-00', # requires registration in lims
                        job = 'harness_test_lims', # also needs registration
                        version = 'v0',
                        operator = 'bv')
    print 'Registered as jobid %d' % res.jobid
    time.sleep(1)

    for step in [x for x in Job.report_as if x]:
        print 'Updating step: "%s"...' % step,
        ret = res.update(jobid = res.jobid,
                         stamp = time.time(),
                         step = step,
                         status = "")
        print ret
        time.sleep(1)

    summary = {'schema_name':'fileref',
               'schema_version':0,
               "path": '/dev/null',
               "sha1": 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
               "size": 0,
               }
    ret = res.ingest(summary)
    print ret

    global a_job_id
    a_job_id = res.jobid
    return

def notest_reregister():
    'This is currently not implemented in real LIMS'
    global a_job_id
    if a_job_id is None:
        return
    ls = lims.Results(lims_url)
    s = ls.reregister(a_job_id)
    print s

if __name__ == '__main__':
    test_register()
    #test_reregister()

'''
LSST CCD Acceptance Testing Running of Jobs
===========================================

'''

import remote

class Job(object):
    '''
    Encapsulate a job.

    This object

    - is given an instance of a lcatr.harness.Config class specifying
      standard input job parameters.

    - configures test software runtime environment

    - runs the test software 

    - runs the validation software

    - marshals the resulting files to the archive

    - feeds the LIMS ingest process
    '''
    
    def __init__(self, cfg):
        '''
        Create a test job.
        '''
        if not cfg.complete():
            raise ValueError,'Given incomplete configuration.'
        self.cfg = cfg
        return

    def archive_exists(self):
        '''
        Return True if archive directory exists.
        '''
        s,o,e = remote.stat(path)
        if s: return False
        o = o.strip()
        if not o: return False
        return True



def path(root, ccd_id, test_name, job_id):
    '''
    Return a path into the archive locating the given results.

    This trivial function defines the pattern of the archive file
    system layout.
    '''
    return '/'.join([str(x) for x in [root, ccd_id, test_name, job_id]])

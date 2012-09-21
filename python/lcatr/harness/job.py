'''
LSST CCD Acceptance Testing Running of Jobs
===========================================

'''

import os
import remote, environment


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
            raise ValueError,'Given incomplete configuration, missing: %s' % \
                cfg.missing()
        self.cfg = cfg
        em = environment.Modules()
        em.guess_setup()
        em.load(cfg.name,cfg.version)
        self.env = em.env
        return

    def archive_exists(self):
        '''
        Return True if archive directory exists.
        '''
        s,o,e = remote.stat(self.cfg.subdir('archive'),
                            self.cfg.archive_host,
                            self.cfg.archive_user)
        if s: return False
        o = o.strip()
        if not o: return False
        return True

    def run(self):
        '''
        Run the main process
        '''

        return

    def validate(self):
        '''
        Run the validation process, return the path to the metadata file.
        '''
        return


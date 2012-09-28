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
    
    required_parameters = [
        'site',       # The (canonical or test) name for a site
        'job',        # Canonical name of the job
        'version',    # Test software version string (git tag) 
        'operator',   # User name of person operating/running the test
        'site',       # Canonical site location where we are running 
        'stamp',      # A time_t seconds stamping when job ran
        'stage_root', # The CCDTEST_ROOT on local machine
        'archive_root', # The CCDTEST_ROOT base of the archive
        'archive_host', # The name of the machine hosting the archive
        'archive_user', # Login name of user that can write to archive
        'unit_type',    # type of unit (eg, CCD/RTM)
        'unit_id',      # The unique unit identifier
        #'job_id',       # The unique job identifer, is figured out here
        ]

    def __init__(self, cfg):
        '''
        Create a test job.
        '''
        if not cfg.complete(Job.required_parameters):
            raise ValueError,'Given incomplete configuration, missing: %s' % \
                cfg.missing(Job.required_parameters)
        self.cfg = cfg
        em = environment.Modules()
        em.setup(cfg.modules_home, cfg.modules_cmd, cfg.modules_version, cfg.modules_path)
        modfile = os.path.join(cfg.job, cfg.version)
        em.load(modfile)
        self.env = em.env
        return

    def archive_exists(self):
        '''
        Return True if archive directory exists.
        '''
        s,o,e = remote.stat(self.cfg.subdir('archive'),
                            self.cfg.archive_host,
                            self.cfg.archive_user)
        if s: 
            print s
            return False
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


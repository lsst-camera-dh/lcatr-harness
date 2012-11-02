'''
LSST CCD Acceptance Testing Running of Jobs
===========================================

'''

import os
from lcatr.harness import remote, environment, lims, util

class Job(object):
    '''
    Encapsulate a job.

    This object

    - is given an instance of a lcatr.harness.Config class specifying
      all job parameters.

    - configures test software runtime environment

    - runs the test software 

    - runs the validation software

    - marshals the resulting files to the archive

    '''

    
    required_parameters = [
        'lims_url',   # Base LIMS URL
        'job',        # Canonical name of the job
        'version',    # Test software version string (git tag) 
        'operator',   # User name of person operating/running the test
        'site',       # Canonical site location where we are running 
        'host',       # Name of host running this job
        'stamp',      # A time_t seconds stamping when job ran
        'stage_root', # The CCDTEST_ROOT on local machine
        'archive_root', # The CCDTEST_ROOT base of the archive
        'archive_host', # The name of the machine hosting the archive
        'archive_user', # Login name of user that can write to archive
        'unit_type',    # type of unit (eg, CCD/RTM)
        'unit_id',      # The unique unit identifier
        ]


    all_steps = ['configure','register','stage','produce','validate', 'archive','purge']


    def __init__(self, cfg):
        '''
        Create a test job with a config.Config object
        '''
        if not cfg.complete(Job.required_parameters):
            raise ValueError,'Given incomplete configuration, missing: %s' % \
                cfg.missing(Job.required_parameters)

        self.cfg = cfg
        self.em = None
        self.lims = None
        return
        
    def run(self, steps = None):
        '''
        Run the job.

        If no steps are given all are run.
        '''
        if not steps:
            steps = self.all_steps
        if isinstance(steps, str):
            steps = [steps]
        for step in steps:
            #print 'Step: "%s"' % step
            meth = eval("self.do_%s" % step)
            try:
                meth()
            except Exception,err:
                if self.lims: self.lims.notify_failure(err)
                raise
            else:
                if self.lims: self.lims.notify_status(step)
            continue
        return
            
    def do_configure(self):
        '''
        Configure the job environment.

        Update order is:

        - calling environment
        - configuration parameter
        - modulefile

        '''
        
        env = dict(os.environ)  # calling environment
        pars = self.cfg.__dict__.iteritems()
        newenv = {'%s%s'%(self.cfg.envvar_prefix,k.upper()):v for k,v in pars}
        env.update(newenv)

        em = environment.Modules(env)
        em.setup(self.cfg.modules_home, self.cfg.modules_cmd, 
                 self.cfg.modules_version, self.cfg.modules_path)
        modfile = os.path.join(self.cfg.job, self.cfg.version)
        print 'Loading modfile: "%s"' % modfile
        em.load(modfile)
        self.em = em
        return

    def do_register(self):
        'Initial registering with lims.'
        self.lims = lims.register(**self.cfg.__dict__)
        return

    def stage_in(**depinfo):
        'Stage in a dependency'
        src = self.cfg.s('%(archive_user)s@%(archive_host)s:%(archive_root)s')
        dst = self.cfg.stage_root
        assert not os.path.exists(dst), 'Directory already exists: "%s"' % dst
        remote.rsync(src,dst)
        return

    def do_stage(self):
        'Ready the stage.'
        for depinfo in self.lims.dependencies(): 
            self.stage_in(**depinfo)
        return

    def do_produce(self):
        out = util.file_logger('producer')
        self.em.execute(self.em.lcatr_producer, out=out.info)
        return

    def do_validate(self):
        out = util.file_logger('validator')
        self.em.execute(self.em.lcatr_validator, out=out.info)
        self.followup_validation()
        return

    def followup_validation(self):
        return

    def do_archive(self):
        return
    
    def do_purge(self):
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


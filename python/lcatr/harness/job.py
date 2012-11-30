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
        'host',       # Name of host running this job
        'stamp',      # A time_t seconds stamping when job ran
        'stage_root', # The CCDTEST_ROOT on local machine
        'archive_root', # The CCDTEST_ROOT base of the archive
        'archive_host', # The name of the machine hosting the archive
        'archive_user', # Login name of user that can write to archive
        'unit_type',    # type of unit (eg, CCD/RTM)
        'unit_id',      # The unique unit identifier
        'install_area', # base to where software is installed
        'modules',      # where the job harnessed modulefiles can be found
        ]


    # The list of steps and how/whether to report to LIMS
    all_steps = ['configure','register','stage','produce','validate','archive','purge']
    report_as = [None,'configured','staged','produced','validated','archived','purged']

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

            stepped = self.report_as[self.all_steps.index(step)]

            util.log.debug('Running step "%s"' % step)
            try:
                meth()
            except Exception,err:
                util.log.error('Error with step %s: %s' % (step,str(err)))
                if self.lims and stepped:
                    self.lims.update(step=stepped,status=err)
                raise
            else:
                util.log.info('Step %s completed' % step)
                if self.lims and stepped: 
                    self.lims.update(step=stepped)
            continue
        return
            
    def do_configure(self):
        '''
        Configure the job environment.

        Update order is:

        - calling environment
        - configuration parameter
        - modulefile

        All parameters are applied by going calling the .em.execute()
        method to execute external programs.
        '''
        
        env = dict(os.environ)  # calling environment
        pars = self.cfg.__dict__.iteritems()
        newenv = {'%s%s'%(self.cfg.envvar_prefix,k.upper()):v for k,v in pars}
        env.update(newenv)

        em = environment.Modules(env)
        em.setup(self.cfg.modules_home, self.cfg.modules_cmd, 
                 self.cfg.modules_version, self.cfg.modules_path)
        modfile = os.path.join(self.cfg.job, self.cfg.version)

        try:
            em.load(modfile)
        except RuntimeError, msg:
            print 'Got runtime error: "%s"' % msg
            for k,v in em.env.iteritems():
                if k.startswith(self.cfg.envvar_prefix):
                    print '%s = %s' % (k,v)
            raise
        self.em = em

        self._check_archive()

        return

    def do_register(self):
        'Initial registering with lims.'
        self.lims = lims.register(**self.cfg.__dict__)
        self.cfg.job_id = self.lims.jobid
        return

    def stage_in(self, **depinfo):
        'Stage in a dependency'

        dst_root = self.cfg.stage_root
        if not os.path.exists(dst_root):
            msg = 'Local stage root directory does not exists: %s' % dst_root
            raise RuntimeError, msg

        path = self.cfg.subdir_policy % depinfo
        src = self.cfg.s('%(archive_user)s@%(archive_host)s:%(archive_root)s/') + path
        dst = os.path.join(dst_root, path)

        if os.path.exists(dst):
            util.log.warning('Directory already staged: "%s"' % dst)
            return

        util.log.info('Staging from "%s" to "%s' % (src, dst))
        rstat = remote.stat(src, host=self.cfg.archive_host, user=self.cfg.archive_user)
        if rstat[0]:
            msg = 'Failed to stat remote archive directory: %s' % src
            raise RuntimeError, msg

        remote.rsync(src,dst)
        return

    def do_stage(self):
        'Ready the stage.'

        wd = self.cfg.subdir('stage')
        if os.path.exists(wd):
            msg = 'Working directory already exists: %s' % wd
            util.log.error(msg)
            raise RuntimeError, msg

        for depinfo in self.lims.prereq:
            self.stage_in(**depinfo)
            continue

        util.log.info('Creating working directory: %s' % wd)
        os.makedirs(wd)

        return

    def go_working_dir(self):
        '''
        Change to the working directory.
        '''
        wd = self.cfg.subdir('stage')
        util.log.debug('Changing to directory: %s' % wd)
        os.chdir(wd)
        return

    def do_produce(self):
        self.go_working_dir()
        #out = util.file_logger('producer')
        self.em.execute(self.em.lcatr_producer, out=util.log.info)
        return

    def do_validate(self):
        self.go_working_dir()
        #out = util.file_logger('validator')
        self.em.execute(self.em.lcatr_validator, out=util.log.info)
        self.followup_validation()
        return

    def followup_validation(self):
        return

    def _check_archive(self):
        '''
        Peak to see if the archive exists.
        '''
        rstat = remote.stat(self.cfg.archive_root,
                            host=self.cfg.archive_host, user=self.cfg.archive_user)
        if rstat[0]:
            msg = 'Remote archive root does not exist: %s@%s:%s' % \
                (self.cfg.archive_user, self.cfg.archive_host,self.cfg.archive_root)
            raise RuntimeError, msg
        return

    def do_archive(self):
        'Archive results of a job.'

        self._check_archive()

        src = self.cfg.subdir('stage') + '/'
        dst = self.cfg.s('%(archive_user)s@%(archive_host)s:')
        dst += self.cfg.subdir('archive') + '/'
        
        if self.archive_exists():
            msg = 'Archive destination directory already exists: %s' % dst
            raise RuntimeError, msg


        util.log.info('Making archive directory "%s' % dst)
        ret = remote.cmd('mkdir -p %s' % self.cfg.subdir('archive'),
                         host=self.cfg.archive_host, user=self.cfg.archive_user)
        if ret[0]:
            raise RuntimeError, \
                'Failed to make archive directory with %d:\nOUTPUT=\n%s\nERROR=\n%s' % ret

        util.log.info('Archiving from "%s" to "%s' % (src, dst))
        ret = remote.rsync(src,dst)
        if ret[0]:
            raise RuntimeError, 'Archive failed with %d:\nOUTPUT=\n%s\nERROR=\n%s' % ret
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


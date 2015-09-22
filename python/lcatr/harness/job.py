'''
LSST CCD Acceptance Testing Running of Jobs
===========================================

'''

import os
from lcatr.harness import remote, environment, lims, util
import lcatr.schema

def log_and_terminal(out):
    print out
    util.log.info(out)

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
        'stage_root', # The LCATR_ROOT on local machine
        'archive_root', # The LCATR_ROOT base of the archive
        'archive_host', # The name of the machine hosting the archive
        'archive_user', # Login name of user that can write to archive
        'unit_type',    # type of unit (eg, CCD/RTM)
        'unit_id',      # The unique unit identifier
        'install_area', # base to where software is installed
        ]


    # The list of steps and how/whether to report to LIMS
    all_steps = ['configure','register','stage','produce','validate','archive','ingest','purge']
    report_as = [None,'configured','staged','produced','validated','archived',None, 'purged']

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
                msg = 'Error with step %s: %s' % (step, err)
                print msg
                util.log.error(msg)
                if self.lims and stepped:
                    ret = self.lims.update(step=stepped,status=msg)
                    if ret:
                        util.log.error(str(ret))
                        print str(ret)
                ix = steps.index(step)
                if (ix > steps.index('configure')) and (ix < steps.index('purge')):
                    self._archive_log()
                raise
            else:
                msg = 'Step %s completed' % step
                print msg
                util.log.info(msg)
                if self.lims and stepped: 
                    ret = self.lims.update(step=stepped)
                    if ret:
                        util.log.error(str(ret))
                        print str(ret)
            continue
        return
            
    def rerun(self, steps = None):
        '''
        Rerun post-registration steps of the job that have not already run.
        '''
        self.do_configure()     # always
        
        # reregister
        self.lims = lims.Results(self.cfg.lims_url)

        #print 'Rerunning with steps: %s' % (', '.join(steps), )
        self.run(steps)
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
        
        self.em = environment.cfg2em(self.cfg)

        modfile = os.path.join(self.cfg.job, self.cfg.version)
        try:
            self.em.load(modfile)
        except RuntimeError, msg:
            print 'Got runtime error: "%s"' % msg
            for k,v in self.em.env.iteritems():
                if k.startswith(self.cfg.envvar_prefix):
                    print '%s = %s' % (k,v)
            raise


        # This needs to be imported so our own attempts at validating
        # the result summary data can find potential schema files.
        if self.em.env.has_key('LCATR_SCHEMA_PATH'):
            os.environ['LCATR_SCHEMA_PATH'] = self.em.env['LCATR_SCHEMA_PATH']
        print 'Loading schema with schema path: "%s"' % \
            self.em.env.get('LCATR_SCHEMA_PATH')
        lcatr.schema.load_all()

        self._check_archive()

        return

    def do_register(self):
        'Initial registering with lims.'
        self.lims = lims.register(**self.cfg.__dict__)
        self.cfg.job_id = self.lims.jobid
        miniDict = {}
        miniDict['LCATR_JOB_ID'] = self.lims.jobid
        self.em.update(miniDict)
        
        return

    def stage_in(self, **depinfo):
        'Stage in a dependency, return path to staged directory'

        dst_root = self.cfg.stage_root
        if not os.path.exists(dst_root):
            msg = 'Local stage root directory does not exists: %s' % dst_root
            raise RuntimeError, msg

        path = self.cfg.subdir_policy % depinfo
        rpath = self.cfg.s("%(archive_root)s/") + path
        src = self.cfg.s('%(archive_user)s@%(archive_host)s:') + rpath
        dst = os.path.join(dst_root, path)


        if os.path.exists(dst):
            util.log.warning('Directory already staged: "%s"' % dst)
            return dst
        os.makedirs(dst)

        util.log.info('Staging from "%s" to "%s' % (src, dst))
        rstat = remote.stat(rpath, host=self.cfg.archive_host, user=self.cfg.archive_user)
        if rstat[0]:
            msg = 'Failed to stat remote archive directory: %s' % src
            raise RuntimeError, msg

        dst = os.path.dirname(dst)
        ret = remote.rsync(src,dst)
        if ret[0]:
            raise RuntimeError, 'Stage in failed with %d:\nOUTPUT=\n%s\nERROR=\n%s' % ret

        return dst

    def do_stage(self):
        'Ready the stage.'

        wd = self.cfg.subdir('stage')
        if os.path.exists(wd):
            msg = 'Working directory already exists: %s' % wd
            util.log.error(msg)
            raise RuntimeError, msg

        deppath = []
        for depinfo in self.lims.prereq:
            depdir = self.stage_in(**depinfo)
            deppath.append(depdir)
            continue

        util.log.info('Creating working directory: %s' % wd)
        os.makedirs(wd)

        (oldname, sep, oldtype) = util.get_logfilepath().partition('.')
        newlog = wd + '/' + oldname + '_' + self.cfg.job_id + sep + oldtype
        util.log.info('Moving log to: %s' % newlog)
        util.move_logfile(newlog)

        self.em.env['LCATR_DEPENDENCY_PATH'] = ':'.join(deppath)
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
        self.em.execute(self.em.lcatr_producer, out=log_and_terminal)
        return

    def do_validate(self):
        self.go_working_dir()
        #out = util.file_logger('validator')
        self.em.execute(self.em.lcatr_validator, out=log_and_terminal)
        self.followup_validation()
        return

    def followup_validation(self):
        self.result = lcatr.schema.validate_file()
        return

    def _check_archive(self, logdir=None):
        '''
        Peek to see if the archive exists. Optionally look for logdir 
        '''
        rdir =self.cfg.archive_root
        if logdir != None: rdir = self.cfg.archivelogdir()
        rstat = remote.stat(rdir,
                            host=self.cfg.archive_host, user=self.cfg.archive_user)
        if rstat[0]:
            msg = 'Remote archive root or logdir does not exist: %s@%s:%s' % \
                (self.cfg.archive_user, self.cfg.archive_host,rdir)
            raise RuntimeError, msg
        return

    def do_archive(self):
        'Archive results of a job.'

        self._check_archive()

        to_archive = 'to_archive'
        src = self.cfg.subdir('stage') + '/'
        # make a to-archive subdirectory.
        if os.path.exists(to_archive):
            raise RuntimeError, 'to-archive subdirectory in staging area already exists'
	os.makedirs(to_archive)
        new_src = src + to_archive + '/'
        # self.result is a list of dicts
        #  Assume it's well-formed by our lights, or we never should have
        #  gotten this far
        for d in self.result:
            if d['schema_name'] == 'fileref':
                path = d['path']
                (dirn, basen) = os.path.split(path)
                destdir = to_archive
                if len(dirn) > 0:
                    destdir = os.path.join(to_archive, dirn)
                    if not os.path.exists(destdir):
                        os.makedirs(destdir)
                os.link(path, os.path.join(destdir, basen))
        os.link('summary.lims', os.path.join(to_archive, 'summary.lims'))
                
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
        util.log.info('Archiving from "%s" to "%s' % (new_src, dst))
        ret = remote.rsync(new_src,dst)
        if ret[0]:
            raise RuntimeError, 'Archive failed with %d:\nOUTPUT=\n%s\nERROR=\n%s' % ret
        ## If it works, clean up with  shutil.rmtree(to_archive)
        return
    
    def do_ingest(self):
        '''
        Upload to lims
        '''
        ret = self.lims.ingest(self.result) # self.result filled in do_validate()
        if ret:
            raise RuntimeError, str(ret)
        
        self._archive_log()
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
            return False
        o = o.strip()
        if not o: return False
        return True

    def _archive_log(self):
        # check if archive log dir already exists; trap error
        try:
            self._check_archive("log")
        except RuntimeError:
            util.log.info('Archive logs directory not found; attempt to create')
            ret = remote.cmd('mkdir -p %s' % self.cfg.archivelogdir(),
                             host=self.cfg.archive_host,
                             user=self.cfg.archive_user)
            if ret[0]: 
                util.log.warning('Failed to make archive log dir with %d:\nOUPUT=\n%s\nERROR=\n%s' % ret)
        
        util.flush_logfile()
        #  scp to archive
        dst = self.cfg.s('%(archive_user)s@%(archive_host)s:')
        dst += self.cfg.archivelogdir() + '/'
        src = util.get_logfilepath()
        cmdstr = "scp -p %s %s" % (src, dst)
        return remote.command(cmdstr)

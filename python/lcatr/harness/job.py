'''
LSST CCD Acceptance Testing Running of Jobs
===========================================

'''
from __future__ import print_function
try:
    from builtins import str
    from builtins import object
except ImportError:
    # builtins not natively in python 2
    pass

import os
from lcatr.harness import remote, environment, lims, util
import lcatr.schema

if os.environ.get('IRODS_ARCHIVE') is None:
    from lcatr.harness import remote
else:
    from lcatr.harness import remote_irods as remote
    
def log_and_terminal(out):
    print(out)
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
        u'lims_url',   # Base LIMS URL
        u'job',        # Canonical name of the job
        u'version',    # Test software version string (git tag) 
        u'operator',   # User name of person operating/running the test
        u'host',       # Name of host running this job
        u'stamp',      # A time_t seconds stamping when job ran
        u'stage_root', # The LCATR_ROOT on local machine
        u'archive_root', # The LCATR_ROOT base of the archive
        u'archive_host', # The name of the machine hosting the archive
        u'archive_user', # Login name of user that can write to archive
        u'unit_type',    # type of unit (eg, CCD/RTM)
        u'unit_id',      # The unique unit identifier
        u'install_area', # base to where software is installed
        ]


    # The list of steps and how/whether to report to LIMS
    all_steps = [u'configure',u'register',u'stage',u'produce',u'validate',u'archive',u'ingest',u'purge']
    report_as = [None,u'configured',u'staged',u'produced',u'validated',u'archived',None, u'purged']

    def __init__(self, cfg):
        '''
        Create a test job with a config.Config object
        '''
        if not cfg.complete(Job.required_parameters):
            raise ValueError('Given incomplete configuration, missing: %s' % \
                cfg.missing(Job.required_parameters))

        self.cfg = cfg
        self.em = None
        self.lims = None
        self.local_validate = False

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
            except Exception as err:
                msg = 'Error with step %s: %s' % (step, err)
                print(msg)
                util.log.error(msg)
                if self.lims and stepped:
                    ret = self.lims.update(step=stepped,status=msg)
                    if ret:
                        util.log.error(str(ret))
                        print(str(ret))

                # I don't know why these steps are excluded.   The old code
                # made a test which made no sense in the rerun case so
                # I changed it to this.
                if step not in ('configure', 'purge', 'ingest'):
                    self._archive_log()
                raise
            else:
                msg = u'Step %s completed' % step
                print(msg)
                util.log.info(msg)
                if self.lims and stepped and (not self.local_validate or step != 'validate'):
                    ret = self.lims.update(step=stepped)
                    if ret:
                        util.log.error(str(ret))
                        print(str(ret))
            continue
        return
            
    def rerun(self, steps = None):
        '''
        Rerun post-registration steps of the job that have not already run.
        '''
        self.do_configure()     # always
        
        # reregister
        self.lims = lims.Results(self.cfg.lims_url)
        self.lims.set_jobid(self.cfg.job_id)

        # In case only ingest is requested, we still need to do validate
        # to generate results, but should skip the handshake with the
        # Front-end
        if steps[0] == 'ingest':
            self.local_validate = True
            steps = ['validate', 'ingest']

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
        except RuntimeError as msg:
            print(u'Got runtime error: "%s"' % msg)
            for k,v in self.em.env.items():
                if k.startswith(self.cfg.envvar_prefix):
                    print(u'%s = %s' % (k,v))
            raise


        # This needs to be imported so our own attempts at validating
        # the result summary data can find potential schema files.
        if u'LCATR_SCHEMA_PATH' in self.em.env:
            os.environ[u'LCATR_SCHEMA_PATH'] = self.em.env[u'LCATR_SCHEMA_PATH']
        print(u'Loading schema with schema path: "%s"' % \
            self.em.env.get(u'LCATR_SCHEMA_PATH'))
        lcatr.schema.load_all()

        self._check_archive()

        return

    def do_register(self):
        'Initial registering with lims.'
        self.lims = lims.register(**self.cfg.__dict__)
        self.cfg.job_id = str(self.lims.jobid)
        miniDict = {}
        miniDict[u'LCATR_JOB_ID'] = str(self.lims.jobid)
        if (self.lims.runNumber != None):
            self.cfg.runNumber = str(self.lims.runNumber)
            miniDict[u'LCATR_RUN_NUMBER'] = str(self.lims.runNumber)
            util.log.info(u'Non-None value for lims runNumber: %s\n' % str(self.lims.runNumber))
        else:
            util.log.info(u'From do_register: no run number found\n')
        if (self.lims.rootActivityId != None):
            self.cfg.rootActivityId = str(self.lims.rootActivityId)
            miniDict[u'LCATR_ROOT_ACTIVITY_ID'] = self.lims.rootActivityId
        self.em.update(miniDict)
        
        return

    def stage_in(self, **depinfo):
        'Stage in a dependency, return path to staged directory'

        dst_root = self.cfg.stage_root
        if not os.path.exists(dst_root):
            msg = u'Local stage root directory does not exists: %s' % dst_root
            raise RuntimeError(msg)
        if  self.lims.runNumber != None:
            # make new dict which includes runNumber
            augmentedinfo = dict(depinfo)
            if self.forceMatch:
                if depinfo[u'runNumber'] != self.lims.runNumber:
                    raise RuntimeError(u'dependent job not in current run')

            augmentedinfo[u'runNumber'] = depinfo[u'runNumber']
            path = self.cfg.run_subdir_policy % augmentedinfo
        else:
            path = self.cfg.subdir_policy % depinfo
        rpath = self.cfg.s(u"%(archive_root)s/") + path
        src = self.cfg.s(u'%(archive_user)s@%(archive_host)s:') + rpath
        dst = os.path.join(dst_root, path)


        if os.path.exists(dst):
            util.log.warning(u'Directory already staged: "%s"' % dst)
            return dst
        os.makedirs(dst)

        util.log.info(u'Staging from "%s" to "%s' % (src, dst))
        rstat = remote.stat(rpath, host=self.cfg.archive_host, user=self.cfg.archive_user)
        if rstat[0]:
            msg = u'Failed to stat remote archive directory: %s' % src
            raise RuntimeError(msg)

        dst = os.path.dirname(dst)
        ret = remote.rsync(src,dst)
        if ret[0]:
            raise RuntimeError(u'Stage in failed with %d:\nOUTPUT=\n%s\nERROR=\n%s' % ret)

        return dst

    def do_stage(self):
        'Ready the stage.'

        wd = self.cfg.subdir(u'stage')
        if os.path.exists(wd):
            msg = u'Working directory already exists: %s' % wd
            util.log.error(msg)
            raise RuntimeError(msg)

        # Find out if we're in Prod database or not
        try:
            intRun = int(self.lims.runNumber)
            self.prod = True
        except (ValueError, TypeError):
            self.prod = False

        self.forceMatch = self.prod
        if os.environ.get(u'LCATR_FORCE_RUN_MATCH') is not None:
            if not self.prod:
                util.log.info(u'LCATR_FORCE_RUN_MATCH is set for non-Prod db')
                self.forceMatch = True

        deppath = []
        for depinfo in self.lims.prereq:
            depdir = self.stage_in(**depinfo)
            deppath.append(depdir)
            continue

        util.log.info(u'Creating working directory: %s' % wd)
        os.makedirs(wd)

        (oldname, sep, oldtype) = util.get_logfilepath().partition('.')
        newlog = wd + u'/' + oldname + '_' + self.cfg.job_id + sep + oldtype
        util.log.info(u'Moving log to: %s' % newlog)
        util.move_logfile(newlog)
        print(u'Moved log to ' + newlog)

        self.em.env[u'LCATR_DEPENDENCY_PATH'] = ':'.join(deppath)
        return

    def go_working_dir(self):
        '''
        Change to the working directory.
        '''
        wd = self.cfg.subdir(u'stage')
        util.log.debug(u'Changing to directory: %s' % wd)
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
        Peek to see if the archive exists. Optionally look for logdir.
        If logdir argument is not empty string, it should start with
        leading /
        '''

        rdir =self.cfg.archive_root
        if logdir != None: rdir = self.cfg.archivelogdir() + logdir
        rstat = remote.stat(rdir,
                            host=self.cfg.archive_host, user=self.cfg.archive_user)
        if rstat[0]:
            msg = u'Remote archive root or logdir does not exist: %s@%s:%s' % \
                (self.cfg.archive_user, self.cfg.archive_host,rdir)
            raise RuntimeError(msg)
        return

    def do_archive(self):
        'Archive results of a job.'

        self._check_archive()

        if self.archive_exists():
            msg = u'Archive destination directory already exists: %s' % dst
            raise RuntimeError(msg)

        # Under some circumstances, just do straight recursive copy to archive
        if self._do_local_copy():  return

        to_archive = u'to_archive'
        src = self.cfg.subdir(u'stage') + u'/'
        # make a to-archive subdirectory.
        if os.path.exists(to_archive):
            raise RuntimeError(u'to-archive subdirectory in staging area already exists')

        os.makedirs(to_archive)
        new_src = src + to_archive + '/'
        # self.result is a list of dicts
        #  Assume it's well-formed by our lights, or we never should have
        #  gotten this far
        for d in self.result:
            if d[u'schema_name'] == u'fileref':
                path = d[u'path']
                (dirn, basen) = os.path.split(path)
                destdir = to_archive
                if len(dirn) > 0:
                    destdir = os.path.join(to_archive, dirn)
                    if not os.path.exists(destdir):
                        os.makedirs(destdir)
                os.link(path, os.path.join(destdir, basen))
        os.link(u'summary.lims', os.path.join(to_archive, u'summary.lims'))
                
        if os.environ.get(u'IRODS_ARCHIVE') is not None:
            dst = "i:"
        else:
            if self.cfg.archive_host != u'localhost':
                dst = self.cfg.s(u'%(archive_user)s@%(archive_host)s:')
            else:
                dst=""
        dst += self.cfg.subdir(u'archive') + u'/'
        
        util.log.info(u'Making archive directory "%s' % dst)
        ret = remote.mkdir(self.cfg.subdir(u'archive'),
                           self.cfg.archive_host, 
                           self.cfg.archive_user)
        if ret[0]:
            raise RuntimeError(u'Failed to make archive directory with %d:\nOUTPUT=\n%s\nERROR=\n%s' % ret)
        util.log.info(u'Archiving from "%s" to "%s' % (new_src, dst))
        
        if os.environ.get(u'IRODS_ARCHIVE') is not None or (self.cfg.archive_host != u'localhost'):
            ret = remote.rsync(new_src,dst)
        else:
            new_src += u'*'
            ret = remote.cp(new_src, dst, True)
        if ret[0]:
            raise RuntimeError(u'Archive failed with %d:\nOUTPUT=\n%s\nERROR=\n%s' % ret)
        ## If it works, clean up with  shutil.rmtree(to_archive)
        return
    
    def do_ingest(self):
        '''
        Upload to lims
        '''
        ret = self.lims.ingest(self.result) # self.result filled in do_validate()
        if ret:
            raise RuntimeError(str(ret))
        
        self._archive_log()
        return

    def do_purge(self):
        return

    def archive_exists(self):
        '''
        Return True if archive directory exists.
        '''
        s,o,e = remote.stat(self.cfg.subdir(u'archive'),
                            self.cfg.archive_host,
                            self.cfg.archive_user)
        if s: 
            return False
        o = o.strip()
        if not o: return False
        return True

    def _archive_log(self):
        # check if archive log dir already exists; trap error
        logdir= '/' + os.path.basename(util.get_logfilepath())[0:7]
        try:
            self._check_archive(logdir)
        except RuntimeError:
            util.log.info(u'Archive logs directory not found; attempt to create')
            ret = remote.mkdir((self.cfg.archivelogdir()+logdir),
                               self.cfg.archive_host,
                               self.cfg.archive_user)
            if ret[0]: 
                util.log.warning(u'Failed to make archive log dir with %d:\nOUPUT=\n%s\nERROR=\n%s' % ret)
        
        util.flush_logfile()
        #  scp to archive unless local
        src = util.get_logfilepath()
        if self.cfg.archive_host == u'localhost' and os.environ.get(u'IRODS_ARCHIVE') is None:
            dst = self.cfg.archivelogdir() + logdir
            return remote.cp(src, dst)
            
        else:
            dst = self.cfg.s(u'%(archive_user)s@%(archive_host)s:')
            dst += self.cfg.archivelogdir() + logdir

            return remote.scp(src, dst)

    # If a) archive_host == 'localhost' and b) there is an empty
    # file in the staging directory named PRESERVE_SYMLINKS
    # then just do cp -pr to archive without hunting through
    # filerefs
    # return True if conditions are satisfied and copy succeeds
    #  else False
    def _do_local_copy(self):
        if self.cfg.archive_host != u'localhost': return False
        special = u'PRESERVE_SYMLINKS'
        if special not in os.listdir(): return False
        if os.stat(special).st_size != 0: return False

        # All conditions met.  Do the copy
        dst = self.cfg.subdir(u'archive') + u'/'
        util.log.info(u'Making archive directory "%s' % dst)
        ret = remote.mkdir(self.cfg.subdir(u'archive'),
                           self.cfg.archive_host, 
                           self.cfg.archive_user)
        
        if ret[0]:
            raise RuntimeError(u'Failed to make archive directory with %d:\nOUTPUT=\n%s\nERROR=\n%s' % ret)
        util.log.info(u'Archiving to "%s' % (dst))

        ret =  remote.cp(u'.', dst, recursive=True)
        if ret[0]:
            raise RuntimeError(u'Failed to make local recursive copy to archive')
        return True

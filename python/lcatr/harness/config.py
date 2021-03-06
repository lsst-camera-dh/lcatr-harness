#!/usr/bin/env python
'''
Configuration of a job
'''
from __future__ import print_function
from __future__ import absolute_import
#from future import standard_library
#standard_library.install_aliases()
#from builtins import str
#from builtins import map
#from builtins import object

import os
import sys
import time
import socket                   # for hostname
from configparser import SafeConfigParser, NoSectionError

from . import environment

def dump_dict(msg,d):
    print(msg)
    for k,v in d.items():
        print(u'\t%s:%s'%(k,v))

def resolve_files(defaults, **kwds):
    files = list(defaults)
    for what in [u'config',u'configs',u'filename',u'filenames']:
        fn = kwds.get(what)
        if not fn: continue
        if isinstance(fn,str): 
            fn = [fn]
        files += fn
        del kwds[what]
        continue
    #print 'Trying files:',' '.join(files)
    files = list(map(os.path.expanduser,files))
    files = list(map(os.path.expandvars,files))
    return files, kwds


class Config(object):
    '''
    The configuration for a job harness instance.
    '''

    envvar_prefix = 'LCATR_'

    # Policy definition of the layout of a result's output relative to
    # ccdtest_root:
    subdir_policy = u'%(unit_type)s/%(unit_id)s/%(job)s/%(version)s/%(job_id)s'
    # Alternate layout when run number is available
    run_subdir_policy = u'%(unit_type)s/%(unit_id)s/%(runNumber)s/%(job)s/%(version)s/%(job_id)s'

    # places to look for RC files.
    default_config_files = [
        '~/.lcatr.cfg',
        './lcatr.cfg',
        ]

    # To be fully configured these parameters must be provided.
    required_parameters = [
        
        'host',  # the name of the host machine running the job
        'local',      # Name for a local environment, used to define others
        'job',        # Canonical name of the job
        'version',    # Test software version string (git tag) 
        'operator',   # User name of person operating/running the test
        'stamp',      # A time_t seconds stamping when job ran
        'stage_root',   # The LCATR_ROOT on local machine
        'archive_root', # The LCATR_ROOT base of the archive
        'archive_host', # The name of the machine hosting the archive
        'archive_user', # Login name of user that can write to archive
        'unit_type',    # type of unit (eg, CCD/RTM)
        'unit_id',      # The unique unit identifier
        'job_id',       # The unique job identifer
        'runNumber',    # The unique run identifier (e.g. 123D)
        'lims_url',     # The URL of the LIMS/eTraveler web service
        'install_area', # base to where software is installed

        'modules_home',         # guessed 
        'modules_version',      # by the
        'modules_cmd',          # environment
        'modules_path',         # module
        ]

    # For iterator script, only container_id and lims_url must be provided.
    # Others come from 'implicit' list
    # COULD also include unit_type, unit_id here.  But eTraveler already
    # includes in each command line it will send iterator.
    required_iterator_parameters = [
        'host',  # the name of the host machine running the job
        'operator',   # User name of person operating/running the test
        'stamp',      # A time_t seconds stamping when job ran
        'stage_root',   # The LCATR_ROOT on local machine
        'install_area', # base to where software is installed
        'modules_home',         # guessed 
        'modules_version',      # by the
        'modules_cmd',          # environment
        'modules_path',         # module
        'container_id', # activity id of container process
        'lims_url',     # URL of eTraveler web service
        ]
  
    # These are not interpreted directly but can be useful for
    # organizing configuration files
    auxiliary_parameters = [
        'context',              # can be used to specify a site/local/job
        'site',                 # can be used to specify a site
        ]

    # These are required but are allowed to be guessed in the code if
    # not specified otherwise.
    allow_implicit = [
        'host',       # guessed based on hostname
        'operator',   # guessed based on USER env var
        'stamp',      # taken as current time
        'stage_root', # taken as current working directory
        'install_area',         # taken as VIRTUAL_ENV/share

        'modules_home',         # guessed 
        'modules_version',      # by the
        'modules_cmd',          # environment
        'modules_path',         # module
        ]



    def __init__(self, **kwds):
        
        cfg = {}

        # all matching environment variables 
        for k,v in os.environ.items():
            if not k.startswith(Config.envvar_prefix): 
                continue
            name = k[len(Config.envvar_prefix):]
            cfg[name.lower()] = v
            continue
        #dump_dict('After environ',cfg)


        # open config file(s) and slurp the [default] section 
        files, kwds = resolve_files(self.default_config_files, **kwds)
        scp = SafeConfigParser()
        used = scp.read(files)
        print('Loaded configuration files:',' '.join(used))
        #dump_dict('Defaults:',scp.defaults())
        cfg.update(scp.defaults())
        #dump_dict('After cfgfile',cfg)
            
        # update based on command line args
        cfg.update(kwds)
        #dump_dict('After kwds:',cfg)

        # Apply section defaults
        def resolve_section(param, value):
            secname = param +' '+ value
            if not scp.has_section(secname): 
                return
            for k,v in scp.items(secname):
                if k in cfg:
                    if v == cfg[k]: continue
                    print(u'Default value of %s = %s overridden by %s' % (k,v,cfg[k]))
                    continue
                cfg[k] = v
                #print '\tnamed section: %s=%s' %(k,cfg[k])
                resolve_section(k,v)
                continue
            return
        for param in list(cfg.keys()):
            value = cfg[param]
            resolve_section(param,value)
            continue
        #dump_dict('After section',cfg)
                    
        self.__dict__.update(cfg)
        #dump_dict('Final', self.__dict__)

        for imp in Config.allow_implicit:
            meth = eval ('self.guess_%s'%imp)
            meth()
            continue

        return

    def s(self, string):
        '''
        Interpolate a string using the parameters.
        '''
        return string % self.__dict__

    def guess_host(self):
        if hasattr(self,'host'): return self.host
        fqdn = socket.gethostbyaddr(socket.gethostname())[0]
        self.host = '.'.join(fqdn.split('.')[-2:])
        return self.host

    def guess_operator(self):
        if hasattr(self,'operator'): return self.operator
        self.operator = os.environ['USER']
        return self.operator

    def guess_stamp(self):
        if hasattr(self,'stamp'): return str(self.stamp)
        self.stamp = str(time.time())
        return self.stamp

    def guess_stage_root(self):
        if hasattr(self,'stage_root'): return str(self.stage_root)
        self.stage_root = os.getcwd()
        return self.stage_root

    def guess_install_area(self):
        if hasattr(self,'install_area'): return str(self.install_area)
        ve = os.environ.get('VIRTUAL_ENV','')
        self.install_area = ve + '/share' if ve else None
        return str(self.install_area)

    def guess_modules_home(self):
        if hasattr(self,'modules_home'): return str(self.modules_home)
        self.modules_home = environment.guess_modules_home()
        return str(self.modules_home)

    def guess_modules_version(self):
        if hasattr(self,'modules_version'): 
            self.modules_version = str(self.modules_version)
            return self.modules_version
        self.modules_version = str(environment.guess_modules_version())
        return self.modules_version

    def guess_modules_cmd(self):
        if hasattr(self,'modules_cmd'): return str(self.modules_cmd)
        self.modules_cmd = environment.guess_modules_cmd()
        return self.modules_cmd

    def guess_modules_path(self):
        if hasattr(self,'modules_path'): return str(self.modules_path)
        self.modules_path = environment.guess_modules_path()
        return str(self.modules_path)

    def complete(self, req = None):
        'Return True if all configuration parameters are specified.'
        req = set(req or Config.required_parameters)
        got = set(self.__dict__.keys())
        return req.issubset(got)

    def missing(self, req = None):
        'Return missing configuration parameters'
        req = set(req or Config.required_parameters)
        got = set(self.__dict__.keys())
        return list(req.difference(got))

    def extra(self, req = None):
        'Return a list of configuration parameter that have been set but are not expected'
        req = set(req or Config.required_parameters)
        got = set(self.__dict__.keys())
        return list(got.difference(req))
        

    def set(self, name, value):
        self.__dict__[name] = value
        return

    def __str__(self):
        comp = "incomplete"
        if self.complete(): comp = "complete"
        ver = self.__dict__.get('version',"")
        return 'Config: "%s" (%s) %s' % (self.name, comp, ver)

    # fixme: these policy methods need to move somewhere else

    def subdir(self, prefix=None):
        '''
        Construct and return the subdir relative to LCATR_ROOT.
        '''
        if prefix == 'archive': prefix = self.archive_root + '/'
        if prefix == 'stage':   prefix = self.stage_root + '/'
        if not prefix:          prefix = ''
        if 'runNumber' in self.__dict__:
            s = Config.run_subdir_policy % self.__dict__
        else:
            s = Config.subdir_policy % self.__dict__
        return prefix + s

    def archivelogdir(self):
        '''
        Construct and return log root dir under archive root
        '''
        return self.archive_root + '/logs'


    def archive_rsync_path(self):
        '''
        Return an rsync'able path for the remote archive LCATR_ROOT
        '''
        s = '%(archive_user)s@%(archive_host)s:%(archive_root)s' % self.__dict__
        return s

    pass


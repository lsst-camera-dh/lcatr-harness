#!/usr/bin/env python
'''
Configuration of a job
'''

import os
import sys
import time
import socket                   # for hostname
from ConfigParser import SafeConfigParser, NoSectionError

def guess_site():
    '''
    Return a site name take as the top two in the FQDN
    '''
    fqdn = socket.gethostbyaddr(socket.gethostname())[0]
    domain = '.'.join(fqdn.split('.')[-2:])
    return domain

def dump_dict(msg,d):
    print msg
    for k,v in d.iteritems():
        print '\t%s:%s'%(k,v)

class Config(object):
    '''
    The configuration for a job harness instance.
    '''

    envvar_prefix = 'LCATR_'

    # Policy definition of the layout of a result's output relative to
    # ccdtest_root:
    subdir_policy = '%(unit_type)s/%(unit_id)s/%(name)s/%(version)s/%(job_id)s'

    # places to look for RC files.
    default_config_files = [
        '~/.lcatr.cfg',
        './lcatr.cfg',
        ]

    # To be fully configured these parameters must be provided.
    required_parameters = [
        
        'context',    # A context, meta parameter used to define others
        'site',       # The (canonical or test) name for a site
        'local'       # Name for a local environment, used to define others
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
        'job_id',       # The unique job identifer
        'modules_home', # Where Modules is installed, sets MODULESHOME
        'modules_version', # Modules installation version
        'modules_cmd',  # the path to the modulescmd program.
        'modules_path', #  adds to MODULEPATH env var
        ]

    def __init__(self, **kwds):
        
        cfg = {}

        # all matching environment variables 
        for k,v in os.environ.iteritems():
            if not k.startswith(Config.envvar_prefix): 
                continue
            name = k[len(Config.envvar_prefix):]
            cfg[name.lower()] = v
            continue
        #dump_dict('After environ',cfg)


        # open config file(s) and slurp the [default] section 
        scp = SafeConfigParser()
        files = list(Config.default_config_files)
        for what in ['config','configs','filename','filenames']:
            fn = kwds.get(what)
            if fn:
                if isinstance(fn,str): 
                    fn = [fn]
                files += fn
                del kwds[what]
                pass
            continue
        #print 'Trying files:',' '.join(files)
        used = scp.read(files)
        #print 'Loaded files:',' '.join(used)
        #dump_dict('Defaults:',scp.defaults())
        cfg.update(scp.defaults())
        #dump_dict('After cfgfile',cfg)
            
        # update based on command line args
        cfg.update(kwds)
        #dump_dict('After kwds:',cfg)

        # Apply section defaults
        def resolve_section(param,value):
            secname = param +' '+ value
            if not scp.has_section(secname): 
                return
            for k,v in scp.items(secname):
                if cfg.has_key(k):
                    if v == cfg[k]: continue
                    print 'Default value of %s = %s overridden by %s' % (k,v,cfg[k])
                    continue
                cfg[k] = v
                #print '\tnamed section: %s=%s' %(k,cfg[k])
                resolve_section(k,v)
                continue
            return
        for param in cfg.keys():
            value = cfg[param]
            resolve_section(param,value)
            continue
        #dump_dict('After section',cfg)
                    
        self.__dict__.update(cfg)
        #dump_dict('Final', cfg)

        return

    def complete(self):
        'Return True if all configuration parameters are specified.'
        req = set(self.required_parameters)
        got = set(self.__dict__.keys())
        return req.issubset(got)

    def missing(self):
        'Return missing configuration parameters'
        req = set(self.required_parameters)
        got = set(self.__dict__.keys())
        return list(req.difference(got))

    def extra(self):
        'Return a list of configuration parameter that have been set but are not expected'
        req = set(self.required_parameters)
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
        Construct and return the subdir relative to CCDTEST_ROOT.
        '''
        if prefix == 'archive': prefix = self.archive_root + '/'
        if prefix == 'local':   prefix = self.local_root + '/'
        if not prefix:          prefix = ''
        s = Config.subdir_policy % self.__dict__
        return prefix + s


    def archive_rsync_path(self):
        '''
        Return an rsync'able path for the remote archive CCDTEST_ROOT
        '''
        s = '%(archive_user)s@%(archive_host)s:%(archive_root)s' % self.__dict__
        return s

    pass


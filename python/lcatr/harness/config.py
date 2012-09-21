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

class Config(object):
    '''
    Encapsulates and builds the configuration for a job.
    '''

    # Policy definition of the layout of a result's output relative to
    # ccdtest_root:
    subdir_policy = '%(ccd_id)s/%(name)s/%(version)s/%(job_id)s'

    # places to look for RC files.
    default_config_files = [
        '~/.lcatr.cfg',
        './lcatr.cfg',
        ]

    # To be fully configured these parameters must be provided.
    required_parameters = [
        
        'name',       # Canonical name of the test station/analysis
        'version',    # Test software version string (git tag) 
        'operator',   # User name of person operating/running the test
        'site',       # Canonical site location where we are running 
        'stamp',      # A time_t seconds stamping when job ran
        'local_root', # The CCDTEST_ROOT on local machine
        'archive_root', # The CCDTEST_ROOT base of the archive
        'archive_host', # The name of the machine hosting the archive
        'archive_user', # Login name of user that can write to archive
        'ccd_id',       # The unique CCD identifier
        'job_id',       # The unique job identifer

        ]

    def __init__(self, name, filename = None, **kwds):
        
        self.name = name

        # sane defaults
        self.operator = os.environ.get('USER')
        self.site = guess_site()
        self.stamp = time.time()
        self.local_root = os.path.curdir

        # Config file gets next chance
        self._cfg = SafeConfigParser()
        self.load(filename)

        # Final chance by caller
        self.__dict__.update(kwds)
        return

    def cfgget(self, section, name):
        try:
            val = self._cfg.get(section, name)
        except NoSectionError, msg:
            #print >> sys.stderr, msg
            return None
        return val

    def load(self, filename = None):
        if not filename:
            filename = self.default_config_files
        #print 'Reading configuration from',filename
        self._cfg.read(filename)

        lr = self.cfgget('local','local_root')
        if lr: self.local_root = lr

        site = self.cfgget('local','site')
        if site: 
            self.site = site

        if self.site:
            for what in ['root','user','host']:
                aname = 'archive_%s' % what
                v = self.cfgget('site %s'%self.site, aname)
                if v: self.__dict__[aname] = v
                continue
            pass

        versions = self.cfgget('local','versions')
        if versions:
            v = self.cfgget('versions %s' % versions, self.name)
            if v: self.version = v
            pass
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

    def set(self, name, value):
        self.__dict__[name] = value
        return

    def __str__(self):
        comp = "incomplete"
        if self.complete(): comp = "complete"
        ver = self.__dict__.get('version',"")
        return 'Config: "%s" (%s) %s' % (self.name, comp, ver)

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


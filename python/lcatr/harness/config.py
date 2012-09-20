#!/usr/bin/env python
'''
Configuration of a job
'''

class Config(object):
    '''
    Encapsulates and builds the configuration for a job.
    '''

    # To be fully configured these parameters must be provided.
    required_parameters = [

        'name',          # Canonical name of the test station/analysis
        'version',       # Test software version string (git tag) 

        'operator',   # User name of person operating/running the test

        'ccd_id',               # The unique CCD identifier
        'stamp',                # A datetime stamping when job ran
        'job_id',               # The unique job identifer

        'archive_directory',    # The CCDTEST_ROOT base of the archive
        'archive_host',         # The name of the machine hosting the archive
        'archive_user',         # Login name of user that can write to archive
        'local_directory',      # Local working directory 

        'process',              # Main process to run
        'validate',             # Validation process
        ]

    def __init__(self, name, version, **kwds):
        self.name  = name
        self.version = version
        self.__dict__.update(kwds)
        return

    def complete(self):
        req = set(self.required_parameters)
        got = set(self.__dict__.keys())
        return req.issubset(got)

    def set(self, name, value):
        self.__dict__[name] = value
        return

    def __str__(self):
        return 'Config: "%s" (%s)' % (self.name, self.version)

    # fixme: add function to load from config file
    pass


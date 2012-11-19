#!/usr/bin/env python
'''
Interface with LIMS
'''

import os
import json
import urllib2
import collections, pickle
import logging
log = logging.getLogger(__name__)

def make_url(base_url, command, **kwds):
    '''
    Return a URL <base_url>/command/?k1=v1&k2=v2
    '''
    args = '&'.join(['%s=%s' % (k,v) for k,v in kwds.iteritems()])
    if base_url[-1] != '/': 
        base_url += '/'
    return base_url + command + '?' + args

class RPC(object):

    def __init__(self, base_url, **reginfo):
        self.base_url = base_url
        self.reginfo = reginfo
        ret = self('register',reginfo)
        self.jobid = ret['jobid']
        self.deps = ret['dependencies']
        return
    
    def __call__(self, command, **kwds):
        url = make_url(self.base_url, command, **kwds)
        log.info('get: "%s"' % url)
        res = urllib2.urlopen(url).read()
        log.info('got: "%s"' % res)
        return json.loads(res)

    pass

        

class FakeTraveler(object):

    default_traveler = {
        ('stage1','v0'): (('stage2','v0'),('ana1','v0')),
        ('stage2','v0'): (('ana2','v0'),),
        }

    def __init__(self, traveler_data = None):
        if not traveler_data: 
            traveler_data = FakeTraveler.default_traveler
        self.traveler = traveler_data
        deps = collections.defaultdict(list)
        for parent, daughters in traveler_data.iteritems():
            print 'parent:"%s", daughters="%s"' % (parent, daughters)
            for d in daughters:
                deps[d].append(parent)
        self.dependencies = deps
    

class FakeLimsDB(object):
    '''
    A fake LIMS database.  
    '''
    
    matched_keys = ['job','version','unit_type','unit_id']

    def __init__(self):
        self.jobs = []          # job registrations
        self.traveler = FakeTraveler()
        return

    def does_match(self, a, b):
        """Return True if a != B but a and b have same values for the matched_keys"""
        if a == b: return False
        n = len(self.jobs)
        if a < 0 or b < 0 or a >= n or b >= n: return false # bad ID

        for m in self.matched_keys:
            try:
                match = a[m] == b[m]
            except KeyError:
                return False
            if not match:
                return False
        return True

    def match_job(self, regid):
        """Return list of regids that match the given one"""
        ret = []
        for ind,job in enumerate(self.jobs):
            if self.does_match(regid, ind):
                ret.append(ind)
        return ret

    def load(self, filename):
        if not os.path.exists(filename):
            self.jobs = []
            return
        fp = open(filename)
        self.jobs = pickle.loads(fp.read())
        fp.close()

    def dump(self, filename):
        fp = open(filename,'w')
        fp.write(pickle.dumps(self.jobs))
        fp.close()

    def register(self, **kwds):
        '''
        Register job information, return tuple of (id, dependencies)
        where ID is the registered identifier and dependencies is a
        list of dictionaries holding the previously registered info
        for all dependent jobs.
        '''
        regid = len(self.jobs)
        self.jobs.append(kwds)

        nv = (kwds['job'],kwds['version'])

        deps = self.traveler[nv]
        depregs = []
        for dep_nv in deps:
            depregs = self.match_job(regid)

        return (regid, depregs)

    pass

class FakeLIMS(object):
    '''
    A fake registered connection to LIMS.
    '''
    def __init__(self, **kwds):
        self.jobid = kwds.get('job_id',"-1")
        return

    def notify_failure(self, msg):
        '''
        Call to notify LIMS of a failure.  Message is error string.
        '''
        print 'Fake LIMS: failure with job %s: "%s"' % (self.jobid, msg)
        return

    def notify_status(self, msg):
        '''
        Call to notify LIMS of a status update.  Message is status string.
        '''
        print 'Fake LIMS: status with job %s: "%s"' % (self.jobid, msg)
        return

    def dependencies(self):
        '''
        Return list of dictionaries of registration information for
        any dependencies this registered job has.
        '''
        return []

def register(**kwds):
    '''
    Return a connection to LIMS
    '''
    return FakeLIMS(**kwds)

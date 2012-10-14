'''
Interface with LIMS
'''

import os
import json
import urllib2

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

        

#!/usr/bin/env python
'''
Interface with LIMS
'''

import time
import json
import urllib

import logging
log = logging.getLogger(__name__)

API = {
    'base_path': 'Results',

    # commands and their query parameters:
    'requestID':['jobid','stamp','unit_type','unit_id', 'job', 'version', 'operator'],
    'update'   :['jobid','stamp','step','status'],
    'ingest'   :['jobid','stamp','result'],

    # details:
    'known_status':[ 'configured','staged','produced','validated','archived','purged'],
    
    }

class Results(object):
    '''
    Register and communicate with the LIMS Results API.

    This follows the LIMS/Harness API document.
    '''


    def __init__(self, url):
        '''
        Create a lims.Register object connected to the given LIMS URL.
        '''
        self.jobid = None
        if url[-1] == '/': url = url[:-1]
        if not url.endswith(API['base_path']):
            url = '/' + API['base_path']
        url += '/'
        self.limsurl = url
        return

    def make_params(self, command, **kwds):
        '''
        Take keyword arguments and return dictionary suitable for use
        with command or raise ValueError.
        '''
        cfg = dict(kwds, stamp=time.time(), jobid=self.jobid)
        want = set(API[command])
        if not want.issubset(cfg):
            raise ValueError, 'Not given enough info needed to register with LIMS'
        query = {k:cfg[k] for k in want}
        return query

    def make_query(self, command, **kwds):
        '''
        Make a query string for the given command and with the given
        keywords or raise ValueError.
        '''
        query = self.make_params(command,**kwds)
        qdata = urllib.urlencode({'jsonObject':json.dumps(query)})
        url = self.limsurl + command
        page = urllib.urlopen(url, qdata).read()
        return json.loads(page)
        

    def register(self, **kwds):
        """
        Register with LIMS.  Call with (at least) the keywords defined
        in API.requestID.  Return LIMS job identifier (or raise
        ValueError) also stored as .jobid.  The list of any
        prerequisites are stored in the .prereq data member.
        """
        res = self.make_query('requestID', **kwds)
        jobid = res['jobid']
        if jobid is None:
            msg = 'Failed to register with LIMS: "%s"' % res['error']
            raise ValueError, msg
        self.jobid = jobid
        self.prereq = res['prereq']
        return jobid

    def update(self, **kwds):
        '''
        Update LIMS that the given <step> has finished.  The <status>
        should be None if the step was successfull, o.w. it should
        explain the error that occured.  Return None if accepted or an
        explanation string if LIMS thinks the caller should terminate.
        '''
        query = self.make_params('update',**kwds)
        if not query['status'] in API['known_status']:
            raise ValueError,'Unknown status update state: "%s"' % query['status']
        res = self.make_query('update', **kwds)
        return res['acknowledge']


    def ingest(self, **kwds):
        '''
        Send a summary <result> list to LIMS.  Return None if accepted
        or an explanation string if LIMS thinks the caller should
        terminate.
        '''
        res = self.make_query('result',**kwds)
        return res['acknowledge']


def register(**kwds):
    '''
    Return a registered Results connection to LIMS
    '''
    res = Results(kwds['limsurl'])
    res.register(**kwds)
    return res


#!/usr/bin/env python
'''
Interface with LIMS
'''
import time
import json
from urllib import urlencode
from urllib2 import urlopen

from util import log

API = {
    'base_path': 'Results',

    # commands and their query parameters:
    'requestID':['jobid','stamp','unit_type','unit_id', 'job', 'version', 'operator'],
    'update'   :['jobid','stamp','step','status'],
    'ingest'   :['jobid','stamp','result'],
    'status'   :['jobid','status'],

    # details:
    'known_steps':[ 'configured','staged','produced','validated','archived','purged'],
    
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
        self.runNumber = None
        self.rootActivityId = None
        if url[-1] == '/': url = url[:-1]
        if not url.endswith(API['base_path']):
            url += '/' + API['base_path']
        url += '/'
        self.lims_url = url
        log.info('Using LIMS URL: "%s"' % url)
        return

    def make_params(self, command, **kwds):
        '''
        Take keyword arguments and return dictionary suitable for use
        with command or raise ValueError.
        '''
        cfg = dict(kwds, stamp=int(time.time()), jobid=self.jobid, 
                   runNumber=self.runNumber, 
                   rootActivityId=self.rootActivityId)
        want = set(API[command])
        missing = want.difference(cfg)
        if missing:
            msg = 'Not given enough info to statisfy LIMS API for %s: missing: %s' % (command, str(sorted(missing)))
            log.error(msg)
            raise ValueError, msg
        query = {k:cfg[k] for k in want}
        return query

    def make_query(self, command, **kwds):
        '''
        Make a query string for the given command and with the given
        keywords or raise ValueError.
        '''
        query = self.make_params(command,**kwds)

        jdata = json.dumps(query)
        qdata = urlencode({'jsonObject':jdata})
        log.debug('Query LIMS "%s" with json="%s", query="%s"' % (command, jdata, qdata))

        url = self.lims_url + command
        
        fp = urlopen(url, data=qdata)
        page = fp.read()
        try:
            jres = json.loads(page)
        except ValueError, msg:
            msg = 'Failed to load return page with qdata="%s" url="%s" got: "%s" (JSON error: %s)' %\
                (qdata, url, page, msg)
            print msg
            log.error(msg)
            raise
        return jres
        

    def register(self, **kwds):
        """
        Register with LIMS.  Call with (at least) the keywords defined
        in API.requestID.  Return LIMS job identifier (or raise
        ValueError) also stored as .jobid.  The list of any
        prerequisites are stored in the .prereq data member.
        """
        res = self.make_query('requestID', **kwds)
        for k in res:
            msg = 'For key %s in res found value res[k]=%s\n' % (k, res[k])
            log.info(msg)
        if 'jobid' not in res:
            if 'error' not in res:
                msg = 'Incomplete response to LIMS register.  No jobid, no error'
                log.error(msg)
                raise ValueError, msg
            else:
                msg = 'Failed to register with LIMs: "%s"' % res['error']
                log.error(msg)
                raise ValueError, msg
        jobid = res['jobid']
        if jobid is None:
            msg = 'Failed to register with LIMS: "%s"' % res['error']
            log.error(msg)
            raise ValueError, msg
        self.jobid = jobid
        if 'runNumber' in res:
            self.runNumber = res['runNumber']
        if 'rootActivityId' in res:
            self.rootActivityId = res['rootActivityId']
        prereq = []
        for pr in res['prereq']:
            # LIMS API specifies "jobid" w/out an underscore, harness has "job_id"
            pr = dict(pr,job_id = pr['jobid'])
            prereq.append(pr)
        self.prereq = prereq
        return jobid

    def reregister(self, jobid):
        """
        Reuse an existing job ID.  This will re-request and set the
        .prereq member and will return the previously updated status
        reports.
        """
        msg = 'Reregistering with jobid=%d' % jobid
        self.jobid = jobid
        print msg
        log.info(msg)
        reg = self.make_query('status', status='registration', jobid=jobid)
        if reg.has_key('error'):
            msg = 'Failed to request registration status for jobid %d (LIMS: %s)' % \
                (jobid, reg['error'])
            log.error(msg)
            raise ValueError, msg

        upd = self.make_query('status', status='update', jobid=jobid)
        if upd.has_key('error'):
            msg = 'Failed to request update status for jobid %d (LIMS: %s)' % \
                (jobid, upd['error'])
            log.error(msg)
            raise ValueError, msg

        assert (jobid == reg['jobid'])

        prereq = []
        for pr in reg['prereq']:
            # LIMS API specifies "jobid" w/out an underscore, harness has "job_id"
            pr = dict(pr,job_id = pr['jobid'])
            prereq.append(pr)
        self.prereq = prereq

        #print upd
        return upd['steps']
        

    def update(self, **kwds):
        '''
        Update LIMS that the given <step> has finished.  The <status>
        should be None if the step was successfull, o.w. it should
        explain the error that occured.  Return None if accepted or an
        explanation string if LIMS thinks the caller should terminate.
        '''
        kwds.setdefault('status',None)
        query = self.make_params('update',**kwds)
        step = query['step']
        if not step in API['known_steps']:
            msg = 'Unknown status update step: "%s"' % step
            log.error(msg)
            raise ValueError, msg
        res = self.make_query('update', **kwds)
        return res['acknowledge']


    def ingest(self, result):
        '''
        Ingest a summary <result> list to LIMS.  Return None if accepted
        or an explanation string if LIMS thinks the caller should
        terminate.
        '''
        res = self.make_query('ingest', result=result)
        return res['acknowledge']


def register(**kwds):
    '''
    Return a registered Results connection to LIMS
    '''
    res = Results(kwds['lims_url'])
    res.register(**kwds)
    return res


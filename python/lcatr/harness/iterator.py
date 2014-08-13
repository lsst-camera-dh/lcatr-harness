#!/usr/bin/env python
'''
Repeatedly query eTraveler for next bit of work, until done.
Similar in some respects to lims.py
'''
import time
import json
from urllib import urlencode
from urllib2 import urlopen

from util import log

from lcatr.harness import environment

class Iterator(object):
    '''
    - object is an instnce of lcatr.harness.Config. Get essential
      parameters from it

    - use parameters to form request to eTraveler for next JH job to
      run, if any

    - loop until no more jobs to run
    '''
    required_parameters = [
        'lims_url',   # Base LIMS URL
        'container_id', # activity id of container process in traveler
        'operator',   # User name of person operating/running the test
        ]

    API = {
        'base_path': 'Results',

        # command and its parameters
        'nextJob' : ['containerid', 'operator'],
        }
    def __init__(self, cfg):
        '''
        Create with a config.Config object
        '''
        if not cfg.complete(Iterator.required_parameters):
            raise ValueError,'Given incomplete configuration, missing: %s' % \
                cfg.missing(Iterator.required_parameters)

        self.cfg = cfg
        self.em = None
        self.request = None

        # to debug without eTraveler
        self.nFake = 3             
        self.iFake = 0

        return

    def createQuery(self, url, command):
        '''
          Get query ready to go.  It's always the same one
        '''
        self.containerid = None
        if url[-1] == '/': url = url[:-1]
        if not url.endswith(self.API['base_path']):
            url += '/' + self.API['base_path']
        url += '/'
        url += command

        self.et_url = url
        log.info('Using eTraveler URL: "%s"' % url)
        query = self.makeParams('nextJob', **self.cfg.__dict__)
        jdata = json.dumps(query)
        self.qdata = urlencode({'jsonObject':jdata})
        log.debug('Query LIMS "%s" with json="%s", query="%s"' % (command, jdata, self.qdata))


    def makeParams(self, command, **kwds):
        '''
        Take keyword arguments and return dictionary suitable for use
        with command or raise ValueError.
        '''
        cfg = dict(kwds, stamp=int(time.time()), 
                   containerid=kwds['container_id'])
        want = set(self.API[command])
        missing = want.difference(cfg)
        if missing:
            msg = 'Not given enough info to statisfy LIMS API for %s: missing: %s' % (command, str(sorted(missing)))
            log.error(msg)
            raise ValueError, msg
        query = {k:cfg[k] for k in want}
        return query


    def getReady(self):
        '''
        create environment from configuration
        make up the http post
        '''
        self.em = environment.cfg2em(self.cfg)
        self.request = self.createQuery(self.cfg.lims_url, 'nextJob')



    def doQuery(self):
        '''
        Execute the query string for the given command and with the given
        keywords or raise ValueError.

        Expected form of return:  an array containing two strings:
        status and command (i.e., next command to execute, if any).
        
        One possible use of these would be
          * status=="DONE" or status=="CMD" both signal success;
            anything else is interpreted as error.   Detailed description
            can go in the second string
          * if  status == "DONE"  we're done!
          * if status == "CMD"  interpret the second string as command
            to be issued
        '''

        # Maybe should enclose in try... in case URLError is thrown?
        # Also check if return is None
        fp = urlopen(self.et_url, data=self.qdata)
        page = fp.read()
        try:
            jres = json.loads(page)
        except ValueError, msg:
            msg = 'Failed to load return page with qdata="%s" url="%s" got: "%s" (JSON error: %s)' %\
                (qdata, self.et_url, page, msg)
            print msg
            log.error(msg)
            raise
        return jres


    def doFakeQuery(self):
        cmdstring = None 
        if self.iFake < self.nFake:
            cmdstring = 'echo Here is command number ' + str(self.iFake)
            status = 'CMD'
            self.iFake += 1
        else:
            status = 'DONE'
            cmdstring =''
        retDict = {'status' : status, 'command' : cmdstring}
        return retDict


    def go(self):
        self.getReady()
        more = True;
        while more:
            res = self.doQuery()
            #res = self.doFakeQuery()
            if res['status'] == 'DONE':
                more = False
                return;
            if res['status'] == 'CMD':
                more = True
                # json data seems to be returned in something
                # which str.split() doesn't handle well
                self.em.execute((res['command']).encode('ascii'))
            else:
                more = False
                # log error?

            
# Define command, maybe called 'nextJob', with argument 'containerId'
# This == activity id of process step containing a sequence of JH steps
#
# Required arguments are
#     * activity id of container step
#     * URL
#     * username 
# They should be available in environment, just as for "regular" lcatr-harness
# command.
#
# return should be two strings: 
#  [status,  command string or error string]
#  Command string is used to run next available step. "Available" means
#     has not been started
#     any preceding steps have been completed 
#  'status' may be 
#  "CMD"   (normal case)
#  "DONE"  (command string is then "" )
#  "FAILED" - or anything else.  (second string is error message)

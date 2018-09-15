#!/usr/bin/env python
'''
Repeatedly query eTraveler for next bit of work, until done.
Similar in some respects to lims.py
'''
from __future__ import print_function
from __future__ import absolute_import
try:
    from future import standard_library
    standard_library.install_aliases()
    #from builtins import str
    from builtins import object
except ImportError:
    pass
    
import time
import json
from urllib.parse import urlencode
from urllib.request import urlopen

from .util import log, log_and_terminal

from lcatr.harness import environment as l_environment

class Iterator(object):
    '''
    - object is an instnce of lcatr.harness.Config. Get essential
      parameters from it

    - use parameters to form request to eTraveler for next JH job to
      run, if any

    - loop until no more jobs to run
    '''
    required_parameters = [
        u'lims_url',   # Base LIMS URL
        u'container_id', # activity id of container process in traveler
        u'operator',   # User name of person operating/running the test
        ]

    API = {
        u'base_path': u'Results',

        # command and its parameters
        u'nextJob' : [u'containerid', u'operator'],
        }
    def __init__(self, cfg):
        '''
        Create with a config.Config object
        '''
        if not cfg.complete(Iterator.required_parameters):
            raise ValueError(u'Given incomplete configuration, missing: %s' % \
                cfg.missing(Iterator.required_parameters))

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
        if not url.endswith(self.API[u'base_path']):
            url += u'/' + self.API[u'base_path']
        url += u'/'
        url += command

        self.et_url = url
        log.info(u'Using eTraveler URL: "%s"' % url)
        query = self.makeParams(u'nextJob', **self.cfg.__dict__)
        jdata = json.dumps(query)
        self.qdata = urlencode({u'jsonObject':jdata})
        log.debug(u'Query LIMS "%s" with json="%s", query="%s"' % (command, jdata, self.qdata))


    def makeParams(self, command, **kwds):
        '''
        Take keyword arguments and return dictionary suitable for use
        with command or raise ValueError.
        '''
        cfg = dict(kwds, stamp=int(time.time()), 
                   containerid=kwds[u'container_id'])
        want = set(self.API[command])
        missing = want.difference(cfg)
        if missing:
            msg = u'Not given enough info to statisfy LIMS API for %s: missing: %s' % (command, str(sorted(missing)))
            log.error(msg)
            raise ValueError(msg)
        query = {k:cfg[k] for k in want}
        return query


    def getReady(self):
        '''
        create environment from configuration
        make up the http post
        '''
        self.em = l_environment.cfg2em(self.cfg)
        self.request = self.createQuery(self.cfg.lims_url, u'nextJob')



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
        fp = urlopen(self.et_url, data=(self.qdata).encode('ascii'))
        page = fp.read()
        try:
            jres = json.loads(page.decode('ascii'))
        except ValueError as msg:
            msg = u'Failed to load return page with qdata="%s" url="%s" got: "%s" (JSON error: %s)' %\
                (self.qdata, self.et_url, page, msg)
            print(msg)
            log.error(msg)
            raise
        return jres


    def doFakeQuery(self):
        cmdstring = None 
        if self.iFake < self.nFake:
            cmdstring = u'echo Here is command number ' + str(self.iFake)
            status = u'CMD'
            self.iFake += 1
        else:
            status = u'DONE'
            cmdstring =''
        retDict = {u'status' : status, u'command' : cmdstring}
        return retDict


    def go(self):
        self.getReady()
        more = True;
        iJob = 1
        while more:
            res = self.doQuery()
            #res = self.doFakeQuery()
            if res[u'status'] == u'DONE':
                print('All child jobs have been run')
                more = False
                return;
            if res[u'status'] == 'CMD':
                more = True
                # json data seems to be returned in something
                # which str.split() doesn't handle well
                print('Begin execution of child job #', iJob)
                #self.em.execute((res['command']).encode(u'ascii'), out=log_and_terminal)
                self.em.execute(str(res['command']), out=log_and_terminal)
                print('Completed execution of child job #', iJob)
                iJob += 1
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

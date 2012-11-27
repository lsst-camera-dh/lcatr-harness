#!/usr/bin/env python
"""
Let's pretend we are LIMS

This provides an HTTP server that tries mightly to pretend to be like
the real LIMS web app.

It should mate with the toy_job_harness:

https://git.racf.bnl.gov/astro/cgit/lcatr/testing/throwe/toy_job_harness.git/
"""

import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import json
import collections
from sys import stderr


import logging
logging.basicConfig(filename='fakelims.log',level=logging.DEBUG)

class FakeTraveler(object):

    default_traveler = {
        ('example_station_A','v0'): (('example_station_B','v0'),('example_ana_A','v0')),
        }

    def __init__(self, traveler_data = None):
        if not traveler_data: 
            traveler_data = FakeTraveler.default_traveler
        self.traveler = traveler_data
        deps = collections.defaultdict(list)
        for parent, daughters in traveler_data.iteritems():
            logging.debug('parent:"%s", daughters="%s"' % (parent, daughters))
            for d in daughters:
                deps[d].append(parent)
        self.dependencies = deps
        return
    def __str__(self):
        return '<FakeTraveler traveler="%s" dependencies="%s">' % \
            (self.traveler, self.dependencies)

    def prereq(self, name, version):
        return self.dependencies.get((name,version))

    pass

class FakeLimsDB(object):
    '''
    A fake LIMS database for testing the job harness
    '''
    def __init__(self, path):
        self.jobregs = []       # dictionaries of job parameters
        self.status = collections.defaultdict(list) # indexed by jobids

    def register(self, **kwds):
        """
        Register a jobs information, return job ID
        """
        jobid = len(self.jobregs)
        self.jobregs.append(kwds)
        return jobid

    def registration(self, jobid):
        """
        Return registration information for given jobid
        """
        try:
            reg = self.jobregs[jobid]
        except IndexError:
            return None
        return reg

    def lookup(self, **kwds):
        """
        Return first jobid that matches given keyword arguments.
        """
        logging.debug('JOBREGS: %s' % str(self.jobregs))

        tomatch = set(kwds.items())
        logging.debug('TOMATCH: %s' % str(tomatch))
        for ind, jr in enumerate(self.jobregs):
            jrs = set(jr.items())
            logging.debug('JR: %s' % str(jrs))
            if tomatch.issubset(jrs):
                return ind
        return None
        
    def update(self, jobid, state, status):
        """
        Update the status of the jobid
        """
        self.status[jobid].append((state,status))
        return

    pass

class FakeLimsCommands(object):
    
    API = {
        'requestID':      ['stamp','unit_type','unit_id', 'job', 'version', 'operator'],
        'update': ['jobid','stamp','step','status'],
        'ingest': ['jobid','stamp','result']
        }

    def __init__(self):
        dbfile = os.path.splitext(__file__)[0] + '.db'
        self.db = FakeLimsDB(dbfile)
        self.traveler = FakeTraveler()
        logging.debug('TRAVELER: "%s"' % str(self.traveler))
        return

    def __call__(self, cmd, **kwds):
        meth = eval('self.cmd_%s'%cmd)
        return meth(**kwds)

    def cmd_requestID(self, unit_type, unit_id, job, version, operator, stamp, jobid=None):
        "Register a job, get a job ID"

        ret = []
        prereqs = self.traveler.prereq(job, version)
        logging.debug('PREREQS=%s' % str(prereqs))

        if prereqs:
            for pr in prereqs:
                jn,jv = pr
                tofind = dict(unit_type=unit_type, unit_id=unit_id, job=jn, version=jv)
                jid = self.db.lookup(**tofind)
                if jid is None:
                    return {'jobid':None, 
                            'error':'Failed to find prerequisite: %s'%str(tofind)}
                job_info = self.db.registration(jid)
                ret.append(job_info)
                continue

        jobid = self.db.register(unit_type=unit_type, unit_id=unit_id, 
                                 job=job, version=version, operator=operator)
        return {'jobid':jobid, 'prereq':prereqs}

    def cmd_update(self, step, status, stamp, jobid):
        "Update status for jobid step"
        self.db.update(jobid, step, status)
        return {'acknowledge', None}

    def cmd_ingest(self, result, stamp, jobid):
        "Ingest the result summary data."
        return {'acknowledge', None}

    pass

lims_commands = FakeLimsCommands()

class FakeLimsHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        res = 'POST only, man!\n'
        self.wfile.write(res)
        return


    def postvars(self):
        """
        Return a dictionary of query parameters
        """
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        logging.debug('ctype="%s" pdict="%s"' % (str(ctype), str(pdict)))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            return {}
        query = {k:v[0] for k,v in postvars.iteritems()}
        js = query['jsonObject']
        return json.loads(js)

    def do_POST(self):

        # check against API
        cmd = self.path.split('/')[-1]
        try:
            api = lims_commands.API[cmd]
        except KeyError:
            self.set_error('Unknown command: "%s"' % cmd)
            return

        pvars = self.postvars()
        logging.debug('CMD:"%s" POSTVARS:"%s"' % (cmd,pvars))

        required_params = set(api)

        if not required_params.issubset(pvars):
            msg = 'Required params: %s' % str(sorted(required_params))
            log.error(msg)
            self.set_error(msg)
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

        ret = lims_commands(cmd, **pvars)
        logging.info(ret)
        self.wfile.write(json.dumps(ret) + '\n')
        return
        
    def set_error(self, msg):
        # use 412 for prereq not satisfied
        self.send_response(400)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(msg + '\n')
        return

    pass

def main():
    try:
        server = HTTPServer(('', 9876), FakeLimsHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()
if __name__ == '__main__':
    main()

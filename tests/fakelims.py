#!/usr/bin/env python
"""
Let's pretend we are LIMS

This provides an HTTP server that tries mightly to pretend to be like
the real LIMS web app.

It should mate with the toy_job_harness:

https://git.racf.bnl.gov/astro/cgit/lcatr/testing/throwe/toy_job_harness.git/
"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

class FakeLimsHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        res = 'POST only, man!'
        self.wfile.write(res)
        return

    def do_POST(self):
        cmd = self.path.split('/')[-1]
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        print 'CTYPE:',ctype
        print 'PDICT:',pdict
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        print 'POSTED:',postvars
        
        self.send_response(301)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        res = '{"verb":"%s", "path":"%s"}' % (what, self.path)
        print res
        self.wfile.write(res)
        return

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

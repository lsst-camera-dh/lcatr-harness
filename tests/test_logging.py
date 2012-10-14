#!/usr/bin/env python

import sys
import logging
import logging.handlers

def test_http():
    '''
    Requires something listening, like:
    nc -l -p 8910
    '''
    log = logging.getLogger('test_http')
    log.setLevel(logging.DEBUG)

    sh = logging.StreamHandler(sys.stderr)
    log.addHandler(sh)
    
    hh = logging.handlers.HTTPHandler("localhost:8910",
                                      "",'GET')
    log.addHandler(hh)

    log.info('Hello World')
    

    

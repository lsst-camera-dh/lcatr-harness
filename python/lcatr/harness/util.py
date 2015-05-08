#!/usr/bin/env python
'''
General utility stuff
'''

import logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

# Set up general, lcatr.harness-wide log
def _setlog(level):
    name = 'lcatr_harness'
    filename = name + '.log'
    l = logging.getLogger(name)

    fh = logging.FileHandler(filename)
    l.addHandler(fh)

    fmt = logging.Formatter('%(asctime)s %(name)s(%(levelname)s) %(message)s')
    fh.setFormatter(fmt)

    l.setLevel(level)


    print 'logging to: %s' % filename
    return l
# fixme: change to INFO in production
log = _setlog(logging.DEBUG)



def file_logger(name, filename = None, level = logging.DEBUG):
    '''
    Make a logger to file of the given name.  If filename is not given
    it is made by appending ".log" to the name.
    '''
    if not filename: 
        filename = name + '.log'
    log = logging.getLogger(name)
    fh = logging.FileHandler(filename)
    log.addHandler(fh)
    log.setLevel(level)
    return log

def log_and_terminal(out):
    print out
    log.info(out)



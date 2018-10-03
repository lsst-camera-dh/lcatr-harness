#!/usr/bin/env python
'''
General utility stuff
'''
from __future__ import print_function
from builtins import object

import logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
import datetime
import string
import shutil
from lcatr.harness.version import __version__

class MovableLogger(object):
    '''
    Provide service to move log to a new location
    '''
    def __init__(self, name='lcatr_harness', level=logging.DEBUG, path=None):
        self.filepath = path;
        self.level = level
        if self.filepath==None:
            now_iso = datetime.datetime.now().isoformat()
            now_iso = ''.join(now_iso.split(':'))
            #now_iso = string.join(string.split(now_iso, ':'), '')
            self.filepath = 'us'.join(now_iso.split('.')) + '.log'
            #print('From MovableLogger __init__ filepath is: ', self.filepath)
            #self.filepath = string.join(string.split(now_iso, '.'), 'us') + '.log'

        self.l = logging.getLogger(name)

        self.fh = logging.FileHandler(self.filepath)
        self.fmt = logging.Formatter('%(asctime)s %(name)s(%(levelname)s) %(message)s')
        self.fh.setFormatter(self.fmt)
        self.fh.setLevel(level)

        self.l.addHandler(self.fh)

        self.l.setLevel(level)

        print('logging to: %s' % self.filepath)
        self.info('lcatr harness version %s' % __version__)
        return

    def flush_lf(self):
        self.fh.flush();

    def get_lfp(self):
        return self.filepath

    def move_lf(self, newpath):
        self.fh.close()
        self.l.removeHandler(self.fh)
        shutil.move(self.filepath, newpath, copy_function=shutil.copy)
        self.filepath = newpath
        newfh = logging.FileHandler(newpath)
        newfh.setFormatter(self.fmt)
        newfh.setLevel(self.level)
        self.l.addHandler(newfh)
        self.fh = newfh

    def debug(self, msg):
        self.l.debug(msg)

    def info(self, msg):
        self.l.info(msg)

    def warning(self, msg):
        self.l.warning(msg)

    def error(self, msg):
        self.l.error(msg)

    def critical(self, msg):
        self.l.critical(msg)

    def log(self, lvl, msg):
        self.l.log(lvl, msg)

# fixme: change to INFO in production
level = logging.DEBUG
log = MovableLogger('lcatr_harness', level)

def get_logfilepath():
    return log.get_lfp()

def move_logfile(newpath):
    return log.move_lf(newpath)

def flush_logfile():
    return log.flush_lf()


def log_and_terminal(out):
    print(out)
    log.info(out)



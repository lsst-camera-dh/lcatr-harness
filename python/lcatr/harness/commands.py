#!/usr/bin/env python
'''
Execute other programs.
'''
from __future__ import absolute_import

import os
from subprocess import Popen, PIPE, STDOUT
from .util import log

class CommandFailure(Exception):
    'Thrown when a command fails to run successfully'
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    pass

def noop(line): return

def execute(cmdstr, env = None, out = None):
    '''
    Execute the given command string.  Return the exit code.

    If "env" is given it is used as an environment dictionary for the
    execution, o.w. os.environ will be used.

    If "out" is given it will be called once with each line of output
    from the command.  It may be called multiple times as the process
    runs.  Any trailing newline on a line is stripped.

    OSError may be raised if cmdstr can not be executed.

    CommandFailure is raised if return value is nonzero.
    '''

    #print('Type of cmdstr is ', type(cmdstr) )
    if type(cmdstr) == type(""):
        cmdstr = cmdstr.strip().split()

    if not env:
        env = os.environ

    if not out:
        out = noop

    def slurp(line):            # send line to all outs
        if line[-1] == '\n':
            line = line[:-1]
        out(line)
        return

    log.debug('Executing: %s' % ' '.join(cmdstr))
    try:
        proc = Popen(cmdstr, stdout=PIPE, stderr=STDOUT, 
                     universal_newlines=True, env=env)
    except OSError as err:
        log.warning(err)
        log.warning('cmd: "%s"' % ' '.join(cmdstr))
        raise

    
    # While command is polled as running, slurp its output and marshal
    # it to out() until command finishes
    res = None
    while True:
        oline = proc.stdout.readline()
        res = proc.poll()

        if oline:
            slurp(oline)

        if res is None:         # still running
            continue

        for line in proc.stdout.readlines():
            slurp(line)         # drain any remaining

        break

    if res == 0: 
        log.debug('Command: "%s" succeeded' % ' '.join(cmdstr))
        return
    err = 'Command: "%s" failed with code %d' % (' '.join(cmdstr), res)
    log.warning(err)
    log.warning('Running environment:\n\t%s' % '\n\t'.join(['%s: %s'%i for i in sorted(env.items())]))
    raise CommandFailure(err)



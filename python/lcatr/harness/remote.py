#!/usr/bin/env python 
'''
Handle accessing remote hosts

'''
from __future__ import absolute_import
try:
    from builtins import str
except ImportError:
    # builtins not natively in python 2
    pass

import os
import subprocess
from .util import log
import time

ssh_command = "ssh -x"             # rely on it being in PATH

def command(cmdstr, retries=2):
    '''
    Run a command return (status,out,err)
    By default allow for 1 extra attempt
    '''
    sleepInterval = 2
    while retries:
        log.info('Executing command: %s, trials remaining: %s' % (cmdstr, 
                 str(retries-1)))
        proc = subprocess.Popen(cmdstr, shell=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = proc.communicate()
        status = proc.poll()
        retries -= 1
        if status == 255: 
            if retries == 0:
                raise RuntimeError('SSH cmd "%s" failed.' % (cmdstr))
            else:
                log.info('SSH cmd "%s" failed. Retrying in %s seconds.' % (cmdstr, str(sleepInterval) ) )
                time.sleep(sleepInterval)
        else: retries=0

    log.info('Command returned status %d, out="%s" err="%s"' % (status,out,err))
    return status,out,err

def cmd(cmdstr, host = "localhost", user = os.environ.get('USER'), retries=2):
    '''
    Run cmd on remote as user@host via SSH *unless* host is "localhost"
    and user is current user.  In that case just run command locally

    Return triple of (status, stdout, stderr).

    If a failure at the SSH level (SSH return code 255) occurs
    RuntimeError is raised.
    '''
    if isinstance(cmdstr,list): cmdstr = ' '.join(cmdstr)

    # If host is localhost and user is current user, don't bother with ssh
    if (host == "localhost") and (user == os.environ.get('USER')):
        thecmd = cmdstr
        #print "Executing local command ", thecmd
    else:
        thecmd = "%s %s@%s %s" % (ssh_command, user, host, cmdstr)
    return command(thecmd, retries)

def stat(path, host = "localhost", user = os.environ.get('USER')):
    '''
    Return output of the "stat" command run as user@host.

    See cmd() for return values. 
    '''
    return cmd("stat %s" % path,host,user)


def rsync(src,dst):
    '''
    Copy a remote file/dir "src" to a destination "dst".
    '''
    cmdstr = "rsync -a %s %s" % (src, dst)
    return command(cmdstr)

def mkdir(target_dir, host, user):
    '''
    Execute mkdir on a remote <user>@<host> connection
    if it really *is* remote or a different user. Else just 
    make the dir
    '''
    if (host != 'localhost') or (user != os.environ.get('USER')):
        cmdstr = 'mkdir -p %s' % target_dir
        return cmd(cmdstr, host, user)

    try:
        #print "Trying to make local directory ", target_dir
        os.makedirs(target_dir)
        return 0,'',''
    except Exception as err:
        return 1,'', err


def scp(src, dst):
    cmdstr = "scp -p %s %s" % (src, dst)
    return command(cmdstr)

def cp(src, dst, recursive=False):
    if recursive:
        cmdstr = "cp -rp %s %s" % (src, dst)
    else:
        cmdstr = "cp -p %s %s" % (src, dst)
    #print "Doing local copy ", src, " to ", dst
    return command(cmdstr)

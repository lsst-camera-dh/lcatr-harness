#!/usr/bin/env python 
'''
Handle accessing remote hosts

'''

import os
import subprocess
from util import log

ssh_command = "ssh -x"             # rely on it being in PATH

def command(cmdstr):
    '''
    Run a command return (status,out,err)
    '''
    log.info('Executing command: %s' % cmdstr)
    proc = subprocess.Popen(cmdstr, shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = proc.communicate()
    status = proc.poll()
    if status == 255: 
        raise RuntimeError,'SSH cmd "%s" failed.' % (cmdstr)
    log.info('Command returned status %d, out="%s" err="%s"' % (status,out,err))
    return status,out,err

def cmd(cmdstr, host = "localhost", user = os.environ.get('USER')):
    '''
    Run cmd on remote as user@host via SSH.

    Return triple of (status, stdout, stderr).

    If a failure at the SSH level (SSH return code 255) occurs
    RuntimeError is raised.
    '''
    if isinstance(cmdstr,list): cmdstr = ' '.join(cmdstr)

    sshcmd = "%s %s@%s %s" % (ssh_command, user, host, cmdstr)
    return command(sshcmd)

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



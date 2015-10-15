#!/usr/bin/env python 
'''
Handle accessing remote hosts

'''

import os
import subprocess
from util import log

ssh_command = "ssh -x"             # rely on it being in PATH

def command(cmdstr, retries=1):
    '''
    Run a command return (status,out,err)
    '''
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
                raise RuntimeError,'SSH cmd "%s" failed.' % (cmdstr)
            else:
                log.info('SSH cmd "%s" failed. Retrying.' % (cmdstr) )
        else: retries=0

    log.info('Command returned status %d, out="%s" err="%s"' % (status,out,err))
    return status,out,err

def cmd(cmdstr, host = "localhost", user = os.environ.get('USER'), retries = 1):
    '''
    Run cmd on remote as user@host via SSH.

    Return triple of (status, stdout, stderr).

    If a failure at the SSH level (SSH return code 255) occurs
    RuntimeError is raised.
    '''
    if isinstance(cmdstr,list): cmdstr = ' '.join(cmdstr)

    sshcmd = "%s %s@%s %s" % (ssh_command, user, host, cmdstr)
    return command(sshcmd, retries)

def stat(path, host = "localhost", user = os.environ.get('USER')):
    '''
    Return output of the "stat" command run as user@host.

    See cmd() for return values. 
    '''
    return cmd("stat %s" % path,host,user, retries=2)


def rsync(src,dst):
    '''
    Copy a remote file/dir "src" to a destination "dst".
    '''
    cmdstr = "rsync -a %s %s" % (src, dst)
    return command(cmdstr)



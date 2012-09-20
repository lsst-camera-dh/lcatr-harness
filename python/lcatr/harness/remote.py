#!/usr/bin/env python 
'''
Handle accessing remote hosts

'''

import os
import subprocess

ssh_command = "ssh"             # rely on it being in PATH

def cmd(cmd, host = "localhost", user = os.environ.get('USER')):
    '''
    Run cmd on remote as user@host via SSH.

    Return triple of (status, stdout, stderr).

    If a failure at the SSH level (SSH return code 255) occurs
    RuntimeError is raised.
    '''
    if isinstance(cmd,list): cmd = ' '.join(cmd)

    sshcmd = "%s %s@%s %s" % (ssh_command, user, host, cmd)

    proc = subprocess.Popen(sshcmd, shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = proc.communicate()
    status = proc.poll()
    if status == 255: raise RuntimeError,'SSH cmd "%s" failed.' % (cmd)
    return status,out,err

def stat(path, host = "localhost", user = os.environ.get('USER')):
    '''
    Return output of the "stat" command run as user@host.

    See cmd() for return values. 
    '''
    return cmd("stat %s" % path,host,user)



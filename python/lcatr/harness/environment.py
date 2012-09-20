#!/usr/bin/env python
'''
Handle environment.
'''

import os
import re
import subprocess
from glob import glob

def guess_modules_home():
    '''
    Try to find where modules are installed.  If successful return a tuple:

    (modcmd,modhome,modver)

    Or None if we fail to find it.
    '''

    mh = os.environ.get('MODULESHOME')
    mv = os.environ.get('MODULE_VERSION')
    if mh and mv: 
        return (os.path.join(mh,'bin/modulecmd'),mh,mv)

    # Debian system installation
    if os.path.exists('/etc/debian_version') and os.path.exists('/usr/bin/modulecmd'):
        vers = glob('/usr/share/modules/Modules/*')
        vers.sort()
        ver = os.path.basename(vers[-1])
        return ('/usr/bin/modulecmd', '/usr/share/modules', ver)

    # go fishing
    maybe = [
        '/opt/lsst/SL53/Modules/*/init', # RACF astro cluster
        '$HOME/opt/modules/Modules/*/init', # 
        ]
    inits = reduce(lambda x,y:x+y, [glob(os.path.expandvars(p%'init')) for p in maybe])
    if not inits: return None
    
    for initdir in inits:
        verdir = os.path.dirname(initdir)
        ver = os.path.basename(verdir)
        modcmd = os.path.join(verdir,'bin/modulecmd')
        if not os.path.exists(modcmd):
            continue
        return (modcmd, verdir, ver)
    return None

def module_name(test_name, test_version = ""):
    '''
    Build module name.

    This defines the expected construction of environment module names.
    '''
    return '-'.join(test_name, test_version)

class Modules(object):
    '''
    Interface to environment modules (modules.sf.net)
    '''
    def __init__(self, env = None):
        '''
        Make interface to environment modules.

        env provides dictionary of initial environment, else os.environ is used

        The resulting object maintaines a .env dictionary of
        environment variables.  Subsequent functions modify it.
        '''

        mod_chv = guess_modules_home()
        if not mod_chv:
            raise RuntimeError,'Failed to find modules home.'

        modcmd,modhome,modver = mod_chv
        self.cmdstr = modcmd

        modpath = []
        try:
            fp = open(os.path.join(modhome, 'init/.modulespath'))
        except IOError:
            pass
        else:
            for line in fp.readlines():
                line = re.sub("#.*$", '', line)
                line = line.strip()
                if not line: continue
                line = re.sub('\$MODULE_VERSION', modver, line)
                modpath.append(line)
                continue
            pass

        self.env = {}
        if env: self.env.update(env)
        else:   self.env.update(os.environ)

        # module.sf.net specific variables cribbed from init/* files
        self.env.update({
            'MODULESHOME': modhome,
            'MODULE_VERSION': modver,
            'MODULE_VERSION_STACK': modver,
            'MODULEPATH': ':'.join(modpath),
            'LOADEDMODULES': '',
            })
        return

    def command(self, flavor, *args):
        '''
        Run: "modulecmd flavor [args]" and return its stdout.

        A RuntimeError is raised if there is a processing error
        '''
        if type(args[0]) == type([]):
            args = args[0]
        else:
            args = list(args)
        proc = subprocess.Popen([self.cmdstr, flavor] + args,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE,
                                env = self.env)
        out,err = proc.communicate()
        #print 'OUT:\nVVV\n%s\n^^^' % out
        #print 'ERR:\nVVV\n%s\n^^^' % err
        status = proc.poll()
        if status: 
            raise RuntimeError,err
        return out

    def do_cmd(self, cmd, mod_name, *args):
        '''
        Run a modules command for a given module and version.

        Results are reflected in the .env dictionary of environment variables.
        '''
        
        # use flavor "sh" as it's easier to parse and we don't want to
        # operate directly on os.environ like modules tries to force
        # on us.
        shcmds = self.command('sh', cmd, mod_name, *args)


        for line in shcmds.split(';'):
            line = line.strip()
            if not line: continue
            if line.startswith('export '): 
                continue
            if line.startswith('unset '):
                var = line.split()[1]
                del(self.env[var])
                continue
            if '=' in line:
                var,val = line.split('=')
                self.env[var] = val
                continue
            print 'unhandled line: "%s"' % line
            continue
        return
    
    def __getattr__(self, cmd):
        if not cmd in ['load','add','unload','rm']: 
            return self.__dict__[cmd]
        return lambda *args: self.do_cmd(cmd,*args)

    pass


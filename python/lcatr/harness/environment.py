#!/usr/bin/env python
'''
Handle environment.
'''

import os
import re
import subprocess
from glob import glob

guessed_bases = [
    '/opt/lsst/SL53/Modules/[0-9]*',
    '$HOME/opt/modules/Modules/[0-9]*',
    '/usr/share/modules/Modules/[0-9]*',
]

def guess_modules_thing(thing, bases = guessed_bases):
    for base in bases:
        path = os.path.join(base,thing)
        path = os.path.expandvars(path)
        paths = glob(path)
        if not paths: 
            continue
        paths.sort()
        return paths[-1]
    return None

def guess_modules_home():
    '''
    Try to guess a value for MODULESHOME
    '''
    mh = os.environ.get('MODULESHOME')
    if mh: return mh

    got = guess_modules_thing('init')
    if not got: return None
    return os.path.dirname(got)
        
def guess_modules_cmd():
    '''
    Try to guess where the modulecmd program is
    '''
    trial = []
    mh = os.environ.get('MODULESHOME')
    if mh: trial.append(os.path.join(mh,'bin/modulecmd'))
    trial += guessed_bases
    return guess_modules_thing('bin/modulecmd', trial)
    
def guess_modules_version():
    mv = os.environ.get('MODULE_VERSION')
    if mv: return mv
    got = guess_modules_thing('')
    if not got: return None
    return os.path.basename(got)

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

        The given env provides dictionary of initial environment, else
        os.environ is used.

        The resulting object maintaines a .env dictionary of
        environment variables.  Subsequent functions modify it.

        By default it is assumed that the environment needed to run
        modules itself has been defined externally.  See the setup()
        method if this is not to be the case.
        '''
        self.env = {}
        if env: self.env.update(env)
        else:   self.env.update(os.environ)
        return

    def guess_setup(self):
        '''
        Use the guess functions defined in this module to set up the
        environment for modules itself.  Raise RuntimeError if failed.
        '''
        home = guess_modules_home()
        if not home: raise RuntimeError, 'No modules home guessed'

        modcmd = guess_modules_cmd()
        if not modcmd: raise RuntimeError, 'No modules command guessed'

        version = guess_modules_version()
        if not version: raise RuntimeError, 'No modules version guessed'

        self.setup(home, modcmd, version)
        return

    def setup(self, home, cmd = None, version = None):
        '''
        Setup environment needed to run modules itself.

        In a source install it is enough to specify the "home" which
        contains both the init/ sub directory and bin/modulecmd.  This
        is the expected value for $MODULESHOME.  Some installations
        may place the modulecmd in a different directory.  If the
        version is not specified, it is assumed that the leaf
        directory of home gives the version

        The version found is returned or None on failure.

        See also the guess_module_*() functions provided here.
        '''

        if not os.path.exists(home):
            return None

        if not cmd: 
            cmd = os.path.join(home,'bin/modulecmd')
        if not os.path.exists(cmd):
            return None

        if version is None:
            version = os.path.basename(home)

        self.cmdstr = cmd

        self.env.update({
            'MODULESHOME': home,
            'MODULE_VERSION': version,
            'MODULE_VERSION_STACK': version,
            'LOADEDMODULES': '',
            })


        # this is probably dangerous....
        saved_environ = os.environ
        os.environ = self.env

        modpath = []
        try:
            fp = open(os.path.join(home, 'init/.modulespath'))
        except IOError:
            pass
        else:
            for line in fp.readlines():
                line = re.sub("#.*$", '', line)
                line = line.strip()
                if not line: continue
                line = os.path.expandvars(line)
                modpath.append(line)
                continue
            pass

        os.environ = saved_environ

        # module.sf.net specific variables cribbed from init/* files
        self.env['MODULEPATH'] = ':'.join(modpath)

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
        if 'ERROR' in err:      # modulecmd lets errors sneak by w/out an error return code
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
        return lambda name, *args: self.do_cmd(cmd, name, *args)

    pass


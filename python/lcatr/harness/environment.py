#!/usr/bin/env python
'''
Handle environment.
'''

from __future__ import print_function
#from __future__ import absolute_import
#from future import standard_library
#standard_library.install_aliases()
#from builtins import object

import os
import re
import subprocess
from glob import glob
from .util import log

guessed_bases = [
    '$VIRTUAL_ENV/Modules/[0-9]*',
    '/opt/lsst/SL53/Modules/[0-9]*',
    '$HOME/opt/modules/Modules/[0-9]*',
    '/usr/share/modules/Modules/[0-9]*',
]

def guess_modules_thing(thing, bases = guessed_bases):
    '''
    Look for "thing" in list of base directories that may have
    environment variables and will be glob'bed.  If multiple globs,
    return lexically highest.  First fit wins.
    '''
    for base in bases:
        path = os.path.join(base,thing)
        path = os.path.expandvars(path)
        paths = glob(path)
        #print path,paths
        if not paths: 
            continue
        paths.sort()
        return str(paths[-1])
    return ""

def guess_modules_home():
    '''
    Try to guess a value for MODULESHOME
    '''
    mh = os.environ.get('MODULESHOME')
    if mh: return str(mh)

    trial = list(guessed_bases)
    trial += ['/usr/share/modules'] # debian

    got = guess_modules_thing('init', trial)
    if not got: return ""
    return str(os.path.dirname(got))
        
def guess_modules_cmd():
    '''
    Try to guess where the modulecmd program is
    '''
    trial = []
    mh = os.environ.get('MODULESHOME')
    if mh: trial.append(os.path.join(mh,'bin/modulecmd'))
    trial += guessed_bases
    trial += ['/usr']       # debian
    return guess_modules_thing('bin/modulecmd', trial)
    
def guess_modules_version():
    mv = os.environ.get('MODULE_VERSION')
    if mv: return str(mv)
    got = guess_modules_thing('')
    if not got: return ""
    if got[-1] == '/': got = got[:-1]
    ver = os.path.basename(got)
    #print 'got ver:%s from:%s'%(ver,got)
    return str(os.path.basename(ver))

def guess_modules_path():
    ret = str(os.path.expandvars(u"$VIRTUAL_ENV/share"))
    mp = str(os.environ.get('MODULEPATH'))
    if mp:
	ret += ':' + mp

    print('Type of guessed MODULEPATH: ',type(ret))
    return ret

def resolve_modulepath(home, env = None, modpatharg = None):
    """
    Resolve the default modulepath in the way that the "module" command would.
    """
    saved_environ = os.environ
    if env:
        os.environ = env

    print('Type of modpatharg: ', type(modpatharg))
    print('Value of modpatharg:  ', modpatharg)
    if not modpatharg:
        modpath = []
    elif isinstance(modpatharg,str):
        modpath = modpatharg.split(':')
    elif (type(modpatharg) == type(u' ')):
        modpath = str(modpatharg).split(':')
    else:
        modpath = modpatharg

    print('Type of modpath (should be list) : %s', type(modpath))    
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
            print('Type of expandvars line is ', type(line))
            if line not in modpath:
                modpath.append(str(line))
            continue
        pass

    os.environ = saved_environ

    print('Type of modpath as returned (should be list) : %s', type(modpath))    
    return modpath


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
        print('Type of guessed home: ', type(home))
        if not home: raise RuntimeError, 'No modules home guessed'

        modcmd = guess_modules_cmd()
        if not modcmd: raise RuntimeError, 'No modules command guessed'

        version = guess_modules_version()
        print('Result of guess_modules_version has type ', type(version))
        if not version: raise RuntimeError, 'No modules version guessed'

        self.setup(home, modcmd, version)
        return

    def setup(self, home, cmd = None, version = None, modpath = None):
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

        version = str(version)
        print("updating self.env version with type ", type(version))
        self.env.update({
            'MODULESHOME': home,
            'MODULE_VERSION': version,
            'MODULE_VERSION_STACK': version,
            'LOADEDMODULES': '',
            })

        print('after update MODULESHOME env type is ', type(self.env['MODULESHOME']))
        modpath = resolve_modulepath(home, env = self.env, modpatharg = modpath)
        print('Type of modpath returned (should be list) : ', type(modpath))          
        #print('Type of entry: ', type(modpath[0]))
        # insert lcatr job expectations
        modpath += [self.install_area]

        for elt in modpath:
            print('Type of %s is ' % elt, type(elt))

        joined = ':'.join(modpath)
        print('Type of joined is ', type(joined))
        self.env['MODULEPATH'] = ':'.join(modpath)

        print('Type of self.env["MODULEPATH"]: ', type(self.env['MODULEPATH']))
        self.env['LCATR_MODULES'] = self.install_area + '/modulefiles'
        print('type of self.env LCATR_MODULES is ', type(self.env['LCATR_MODULES']))
        return

    def command(self, flavor, *args):
        '''
        Run: "modulecmd flavor [args]" and return its stdout.

        A RuntimeError is raised if there is a processing error
        '''
        out,err,status = self.command_outerr(flavor,*args)

        log.info('OUT:\nVVV\n%s\n^^^' % out)
        log.info('ERR:\nVVV\n%s\n^^^' % err)

        return out

    def command_outerr(self, flavor, *args):
        if type(args[0]) == type([]):
            args = args[0]
        else:
            args = list(args)
        cmd = [self.cmdstr, flavor] + args

        msg = 'Running command: "%s", MODULEPATH="%s"' % \
            (' '.join(cmd), self.env['MODULEPATH'])
        log.info(msg)
        for k,v in self.env.iteritems():
            if (type(k) != str) : print('Key type is %s' % type(k))
            if (type(v) != str) : print('Value type is %s' % type(v))
            assert type(k) == str and type(v) == str, 'bad: %s:%s'%(k,v)
        proc = subprocess.Popen(cmd,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE,
                                env = self.env)
        out, err = proc.communicate()
        status = proc.poll()

        # Check also for 'ERROR' because modulecmd lets errors sneak
        # by w/out an error return code
        if status or 'ERROR' in err:
            msg = '%s\ncmd: "%s" with path: %s' % \
                (err,' '.join(cmd), self.env['MODULEPATH'])
            raise RuntimeError,msg

        return out,err,status

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
            msg = 'unhandled line in interpreting module environment: "%s"' % line
            log.warning(msg)
            print(msg)
            continue
        return
    
    def do_avail(self, *args):
        return self.command_outerr('sh', 'avail', *args)[1]
        

    def __getattr__(self, cmd):
        '''
        If a environment modules command is requested, return a
        callable to execute that command. Otherwise return the value
        of an environment variable of the same name (or an upper cased
        version).  No special name prefix is assumed.
        '''
        if cmd in ['load','add','unload','rm']: 
            return lambda name, *args: self.do_cmd(cmd, name, *args)
        if cmd in ['avail']:
            return lambda *args: self.do_avail(*args)

        var = cmd
        for maybe in [var, var.upper(), 'lcatr_'+var, 'LCATR_'+var.upper()]:
            if self.env.has_key(maybe):
                return self.env[maybe]
        raise KeyError,cmd


    def execute(self, cmdstr, out = log.debug):
        '''
        Execute the command string in the environment.
        '''
        from .commands import execute as comm_execute
        try:
            ret = comm_execute(cmdstr, self.env, out)
        except OSError:
            msg = 'Failed to run: %s' % cmdstr
            print(msg)
            log.error(msg)
            raise

    def update(self, d):
       '''
       Update env
       '''
       self.env.update(d)

    pass

def cfg2em(cfg):

    env = dict(os.environ)  # calling environment
    pars = cfg.__dict__.iteritems()
    newenv = {'%s%s'%(cfg.envvar_prefix,k.upper()):v for k,v in pars}
    env.update(newenv)

    em = Modules(env)

    em.setup(cfg.modules_home, cfg.modules_cmd, 
             cfg.modules_version, cfg.modules_path)

    return em

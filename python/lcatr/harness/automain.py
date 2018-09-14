#!/usr/bin/env python
'''
User interface to the job harness iterator
'''
from __future__ import print_function

import sys
import argparse
from lcatr.harness import config
from lcatr.harness import environment
##from lcatr.harness import job as jobmod   # maybe don't need this
from lcatr.harness import iterator as iteratormod

###non_job_steps = ['help','dump']

def do_help(cfg):
    print('usage: lcatr_auto [options]')
    return 'help called'

def do_dump(cfg):
    print('Configuration:')
    for k,v in sorted(cfg.__dict__.items()):
        print('%s: %s' % (k,v))
    sys.exit(1)

def cmdline(args):
    'LSST job harness sequencer'
    parser = argparse.ArgumentParser(description=cmdline.__doc__)

    parser.add_argument('-c','--config', action='append',
                        help="Add a config file")

    for par in config.Config.required_iterator_parameters:
        # + config.Config.auxiliary_parameters:
        flag = '--' + par.replace('_','-')
        parser.add_argument(flag, default = "")

    ##parser.add_argument('steps', nargs="*")

    optarg = parser.parse_args(args)

    ##steps = []
    kwds = {}
    for opt,arg in optarg.__dict__.items():
        if not arg: continue

        kwds[opt] = arg

    cfg = config.Config(**kwds)
    it = iteratormod.Iterator(cfg)
    it.go()

if '__main__' == __name__:
    it = cmdline(sys.argv[1:])

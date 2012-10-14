#!/usr/bin/env python
'''
User interface to the job harness.

'''

import argparse
from lcatr.harness import config
from lcatr.harness import job as jobmod

def cmdline(args):
    'LSST CCD Aceptance Test Job Harness'
    parser = argparse.ArgumentParser(description=cmdline.__doc__)

    parser.add_argument('-c','--config', action='append',
                        help="Add a config file")

    for par in config.Config.required_parameters:
        flag = '--' + par.replace('_','-')
        parser.add_argument(flag, default = None)

    parser.add_argument('steps', nargs="*")

    opt = parser.parse_args(args)

    steps = None
    if opt.steps:
        steps = opt.steps
        del (opt.steps)

    kwds = {}
    for opt,arg in opt.__dict__.iteritems():
        if arg is None: continue
        kwds[opt] = arg

    cfg = config.Config(**kwds)
    
    job = jobmod.Job(cfg)
    job.run(steps)

if '__main__' == __name__:
    import sys
    job = cmdline(sys.argv[1:])



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

    for par in config.Config.required_parameters + config.Config.auxiliary_parameters:
        flag = '--' + par.replace('_','-')
        parser.add_argument(flag, default = "")

    parser.add_argument('steps', nargs="*")

    optarg = parser.parse_args(args)

    steps = None
    kwds = {}
    for opt,arg in optarg.__dict__.iteritems():
        if not arg: continue
        if opt == "steps":
            steps = arg
            continue
        kwds[opt] = arg

    cfg = config.Config(**kwds)
    
    job = jobmod.Job(cfg)
    job.run(steps)

if '__main__' == __name__:
    import sys
    job = cmdline(sys.argv[1:])



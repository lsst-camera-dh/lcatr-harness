#!/usr/bin/env python
'''
A set of examples to spin through the harness.

Start tests/fakelims.py first
'''

import os
from lcatr.harness import main

def do_main(job):
    here = os.path.dirname(os.path.realpath(__file__))
    cfgfile = here + '/example.cfg'
    main.cmdline(['--config', cfgfile,
                  '--version','v0',
                  '--job', job])
    

def test_1():
    do_main('example_station_A')

def test_2():
    do_main('example_station_B')

def test_3():
    do_main('example_ana_A')

if __name__ == '__main__':
    test_1()
    test_2()
    test_3()




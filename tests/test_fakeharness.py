#!/usr/bin/env python 
'''
A fake job harness to go along with the fake lims server
'''

import os
from lcatr.harness import lims

lims_url = "http://localhost:9876/Results/"


for job in ['example_station_B','example_station_A','example_ana_A']:
    l = lims.register(lims_url = lims_url,
                      unit_type='CCD',
                      unit_id='1-100',
                      job=job,
                      version='v0',
                      operator=os.environ.get('USER'))

    print job,l.jobid,l.prereq

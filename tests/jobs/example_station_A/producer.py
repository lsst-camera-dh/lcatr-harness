#!/usr/bin/env python
"""
Main producer program for example_station_A

This produces a "result" file example_station_A_output.txt with 100
"measurements" of each of 16 amplifiers.
"""

import random

import common

fd = open(common.data_file_name, "w")
for sample in range(100):
    line = ["%12.6f" % random.gauss(x,1) for x in range(16)]
    line = ' '.join(line)
    fd.write(line + '\n')
fd.close()
        

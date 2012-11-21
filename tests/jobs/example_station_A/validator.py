#!/usr/bin/env python
"""
Main validation program for example_station_A

Make sure there are 100 measurements of 16 values and produce required
LIMS interchange files.
"""

import os
import common

n_expected_sample = 100
n_expected_amps = 16

def internal_checks():
    """
    Perform any checks deemed important by the athor of the software
    """
    fd = open(common.data_file_name)
    count = 0
    for lineno,line in enumerate(fd.readlines()):
        line = line.strip()
        if not line: continue
        if line[0] == "#": continue
        vals = line.split()
        nvals = len(vals)
        assert nvals == n_expected_amps, \
            "Got unexpected number of values at line %d: %d" % (lineno, nvals)
        fvals = map(float, vals)    # data should look like numbers
        count += 1
        continue
    assert count == n_expected_sample, \
        "Got unexpected number of measurements: %d != 16" % count
    return

def make_results_summary():
    """
    Make the metadata.fits file.
    """
    import lcatr.schema

    import sys

    # fixme: this schema file needs to be published
    sfile = os.path.join(sys.path[0], "example_station_a.schema")
    lcatr.schema.load(sfile)
    myschema = lcatr.schema.get("example_station_a")

    result_summary = [

        # add reference to the full data file
        lcatr.schema.fileref.make(common.data_file_name),
        
        # we cheat here, 
        lcatr.schema.valid(myschema, 
                           nsamples=n_expected_sample, 
                           namps = n_expected_amps)
        ]
    lcatr.schema.write(result_summary)

def main():
    internal_checks()
    make_results_summary()



if __name__ == '__main__':
    main()

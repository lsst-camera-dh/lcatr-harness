#!/usr/bin/env python
"""
Test the fake lims interface
"""

import os

fake_db_file = os.path.splitext(__file__)[0] + '.db'

from lcatr.harness import lims
limsdb = lims.FakeLimsDB()

def test_load():
    limsdb.load(fake_db_file)


def test_print_db():
    print 'JOBS:', limsdb.jobs
    print 'Traveler:', limsdb.traveler.traveler
    print 'Dependencies:', limsdb.traveler.dependencies


def test_dump():
    limsdb.dump(fake_db_file)

if __name__ == '__main__':
    test_load()
    test_print_db()
    test_dump()

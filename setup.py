#!/usr/bin/env python
from glob import glob
from distutils.core import setup
setup(name='lcatr-harness',
      version='0.1',
      url='https://git.racf.bnl.gov/astro/cgit/lcatr/harness.git',
      author='Brett Viren',
      author_email='bv@bnl.gov',
      package_dir = {'': 'python'},
      packages = ['lcatr','lcatr.harness'],
      data_files = [ 
        ('doc',glob('doc/*.org'))
        ]
      )

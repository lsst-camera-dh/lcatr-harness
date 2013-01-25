#!/usr/bin/env python
from glob import glob
from distutils.core import setup

setup(name='lcatr-harness',
      provides = ["lcatr.harness"],
      requires = ["lcatr"], 
      version='0.2rc',
      url='https://git.racf.bnl.gov/astro/cgit/lcatr/harness.git',
      author='Brett Viren',
      author_email='bv@bnl.gov',
      package_dir = {'': 'python'},
      packages = ['lcatr.harness'],
      scripts = ['scripts/lcatr-harness'],
      data_files = [ 
        ('doc',glob('doc/*.org')),
        ('tests', glob('tests/test_*.py') \
             + glob('tests/test_*.sh') \
             + glob('tests/*.cfg') \
             + ['tests/fakelims.py', 'tests/make-fakeinst.sh'])
        ]
      )

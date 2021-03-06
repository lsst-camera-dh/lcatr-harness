#!/usr/bin/env python
from glob import glob
from distutils.core import setup

setup(name='lcatr-harness',
      provides = ["lcatr.harness"],
      requires = ["lcatr"], 
      version=open('VERSION').read().strip(),
      url='https://git.racf.bnl.gov/astro/cgit/lcatr/harness.git',
      author='Brett Viren',
      author_email='bv@bnl.gov',
      maintainer='Joanne Bogart',
      maintainer_email='jrb@slac.stanford.edu',
      package_dir = {'': 'python'},
      packages = ['lcatr.harness'],
      scripts = ['scripts/lcatr-harness', 'scripts/lcatr-iterator', 
                 'scripts/lcatr-launcher'],
      data_files = [ 
        ('doc',glob('doc/*.org')),
        ('tests', glob('tests/test_*.py') \
             + glob('tests/test_*.sh') \
             + glob('tests/*.cfg') \
             + ['tests/fakelims.py', 'tests/make-fakeinst.sh'])
        ]
      )

#!/usr/bin/env python
import sys
import argparse
import os
import os.path
import shutil
import glob

# packages should be installed under 
#  <root>/lib/pythonMAJ.MIN/site-packages
# where MAJ = sys.version_info.major and MIN = sys.version_info.minor


parser = argparse.ArgumentParser(description='install lcatr/harness')
parser.add_argument('jhRoot', action='store', metavar='root',
                    help='Root of job harness installation')
parser.add_argument('--update', '-u', action='store_true', dest = 'update',
                    default=False,
                    help='allow overwrite of existing installation')
args = parser.parse_args()

jhRoot = vars(args)['jhRoot']
update = vars(args)['update']
pkg = 'lcatr/harness'

pythonversion = 'python' + str(sys.version_info.major) + '.' + str(sys.version_info.minor)
sitePkgs = os.path.join(jhRoot, 'lib', pythonversion, 'site-packages')
if (not os.path.isdir(sitePkgs)) or (not os.path.isdir(os.path.join(jhRoot, 'bin'))):
    print root + ' is not root of a job harness installation'
    sys.exit()

pkgtop = os.path.dirname(sys.argv[0])

installedTop = os.path.join(sitePkgs, pkg)

if os.path.isfile(os.path.join(installedTop, '__init__.py')):
    if not update:
        print 'Some version of the package is already installed'
        print 'Delete or move away before attempting new install'
        print 'or re-invoke with --update option'
        sys.exit()
    else:
        shutil.rmtree(installedTop)
        print 'Old python files removed. Overwriting old version'

if not os.path.isdir(os.path.join(jhRoot, 'doc')):
    os.mkdir(os.path.join(jhRoot, 'doc'))

if not os.path.isdir(installedTop):
    os.makedirs(installedTop)

shutil.copy(os.path.join(pkgtop, 'scripts/lcatr-harness'), 
            os.path.join(jhRoot, 'bin'))
shutil.copy(os.path.join(pkgtop, 'scripts/lcatr-iterator'), 
            os.path.join(jhRoot, 'bin'))

docs = glob.glob(os.path.join(pkgtop, 'doc/*.org'))
for doc in docs:
    shutil.copy(doc, os.path.join(jhRoot, 'doc'))

srcs = glob.glob(os.path.join(pkgtop, 'python/lcatr/harness/*.py'))
for src in srcs:
    shutil.copy(src, installedTop)






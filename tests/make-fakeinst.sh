#!/bin/bash

# build out a fake installation that lets one run the code in-place
# Run this in the directory that holds lcatr/

base=$1 ; shift
if [ -z "$base" ] ; then
    base=$(pwd)/lcatr
fi
base=$(readlink -f $base)
dest=$1 ; shift
if [ -z "$dest" ] ; then
    dest=fakeinst
fi
dest=$(readlink -f $dest)

mklink () {
    src=$1 ; shift
    dst=$1 ; shift

    ln -s $base/$src $dest/$dst
}

mkdir -p $dest/modulefiles
mkdir -p $dest/python/lcatr
touch $dest/python/lcatr/__init__.py

for pkg in harness schema
do
    mklink $pkg/python/lcatr/$pkg python/lcatr/$pkg
done

mklink modulefiles/modules/*      modulefiles
mklink modulefiles/lib/lcatr.tcl  modulefiles/lcatr.tcl
mklink harness/tests              tests

for job in example_station_A example_station_B example_ana_A
do
    mkdir -p $dest/jobs/$job
    mklink jobs/$job jobs/$job/v0
done



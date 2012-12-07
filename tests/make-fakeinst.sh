#!/bin/bash

# build out a fake installation that lets one run the code in-place
# Run this in the directory that holds lcatr/

lcatrurl="https://git.racf.bnl.gov/astro/git/lcatr"

base=$1 ; shift
if [ -z "$base" ] ; then
    base=$(pwd)/lcatr
fi

# get the source code
if [ ! -d $base ] ; then
    mkdir -p $base/jobs
    pushd $base
    for pkg in schema harness modulefiles jobs/example_ana_A jobs/example_station_A jobs/example_station_B
    do
	if [ -d $pkg ] ; then
	    echo "Already have $pkg"
	    continue
	fi

	mkdir $pkg
	pushd $pkg
	git init
	git config credential.helper store
	git remote add central $lcatrurl/${pkg}.git
	git pull central master
	popd
    done
    popd
fi
base=$(readlink -f $base)

# make the install area
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

echo "Source in $base, fake installation in $dest"
echo "Try running:"
echo "cd $dest"
echo "./tests/testrunner test examples"


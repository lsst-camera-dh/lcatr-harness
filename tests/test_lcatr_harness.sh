#!/bin/bash
set -x
if [ -z "$LCATR_INSTALL_AREA" ] ; then
    echo "LCATR_INSTALL_AREA must be defined"
    exit 1
fi

export LCATR_MODULES=$(lcatr-modulefiles-config)

testdir=$(dirname $(readlink -f $BASH_SOURCE))

run_tests () {

    if [ -n "$1" ] ; then
	to_check=""
	for check in $@ ; do
	    fn="$testdir/test_${check}.py"
	    if [ -f $fn ] ; then
		to_check="$to_check $fn"
	    else
		echo "No test for $check"
	    fi
	done
    else
	to_check=$testdir/test_*.py
    fi

    for testpy in $to_check
    do
	log=$(basename $testpy .py).log

        #echo "Running: $testpy logging to $log"
	python $testpy > $log 2>&1
	err=$?
	if [ "$err" = "0" ] ; then
	    echo "Success: $log"
	else
	    echo "FAILURE: $log"
	fi
    done
}
run_tests $@


#!/bin/bash

pkgdir=$(dirname $0)
export PYTHONPATH=$pkgdir/python

if [ -n "$1" ] ; then
    to_check=""
    for check in $@ ; do
	fn="$pkgdir/tests/test_${check}.py"
	if [ -f $fn ] ; then
	    to_check="$to_check $fn"
	else
	    echo "No test for $check"
	fi
    done
else
    to_check=$pkgdir/tests/test_*.py
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

#!/bin/bash

top=$(dirname $BASH_SOURCE)

start_server () {
    local server="python $top/fakelims.py"
    local log=test_fakelims_server.log 
    $server > $log 2>&1 &
    pid=$!
    echo $pid
}

do_one_job () {
    job=$1 ; shift
    unit_id=$1 ; shift

    local regurl="http://localhost:9876/Request/register"
    local regargs="-d version=v0 -d operator=$USER -d unit_id=$unit_id -d unit_type=CCD $regurl"
    echo "Registering $job $unit_id"
    curl -d job=$job $regargs
}

do_one_unit () {
    local unit_id=$1 ; shift

    local regurl=http://localhost:9876/Request/register
    local regargs="-d version=v0 -d operator=$USER -d unit_id=$unit_id -d unit_type=CCD $regurl"
    for job in example_station_A example_station_B example_ana_A
    do
	do_one_job $job $unit_id
	#curl -d job=$job $regargs
    done
}

do_clients () {
    for unit_id in 1-100 1-101 1-102
    do
	do_one_unit $unit_id
    done
}

pid=$(start_server)

sleep 1
do_clients
sleep 1

echo "Killing server PID $pid"
kill $pid








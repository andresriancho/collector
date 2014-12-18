#!/bin/bash

#set -x

# Just in case...
PID=`ps -eaf | grep w3af_console | grep -v grep | awk '{print $2}'`

if [[ "" !=  "$PID" ]]
then
    echo 'Killing w3af_console'
    pkill -9 -f w3af_console
else
    echo 'w3af_console is not running'
fi

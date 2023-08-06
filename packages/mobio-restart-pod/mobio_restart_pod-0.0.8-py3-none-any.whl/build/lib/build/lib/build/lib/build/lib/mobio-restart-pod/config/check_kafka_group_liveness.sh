#!/bin/bash
set -e
result=`python3.8 -u check_kafka_group_liveness_3.py $1`
echo $result
if [ "$result" == "NotWorker" ]; then
    exit 1
else
    exit 0
fi

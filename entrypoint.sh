#!/bin/bash

# Check which Spark mode is being started (master or worker)
if [ "$SPARK_MODE" = "master" ]; then
    echo "Starting Spark master..."
    $SPARK_HOME/sbin/start-master.sh
    tail -f $SPARK_HOME/logs/*
elif [ "$SPARK_MODE" = "worker" ]; then
    echo "Starting Spark worker and connecting to master at $SPARK_MASTER"
    $SPARK_HOME/sbin/start-worker.sh $SPARK_MASTER
    tail -f $SPARK_HOME/logs/*
else
    echo "Unknown Spark mode: $SPARK_MODE. Exiting."
    exit 1
fi

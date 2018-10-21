#!/bin/bash

# variables ${START} and ${END} from reffile
START=1
END=500

# output 
start_smartinizer() {
	#$HOME/build/top-level/dev/analyzers/docker.anaconda/bin/RunLocanaPython.sh runme4.py self -d ct 1 -ref ${START} ${END} -int 30 -rmq amqp://rabbitmq:password@rabbitmq:5672
	$HOME/build/top-level/dev/analyzers/docker.anaconda/bin/RunLocanaPython.sh runme4.py self -d ct 1 -reffile reffile -int 30 -rmq amqp://rabbitmq:password@rabbitmq:5672

}

start_smartinizer

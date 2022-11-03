#!/bin/sh
docker build -t pamw .
docker rm pamw > /dev/null
docker create -p 5050:5050 --name pamw pamw > /dev/null
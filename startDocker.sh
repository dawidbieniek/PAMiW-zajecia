#!/bin/sh
docker image rm pamw-image
docker build -t pamw-image .
docker run --rm -p 5050:5050 --name pamw-container pamw-image 
# docker run --rm -p 5050:5050 --name pamw-container --mount "type=bind,source=$(pwd)/,target=~/" pamw-image


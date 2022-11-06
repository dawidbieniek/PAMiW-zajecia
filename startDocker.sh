#!/bin/sh
# docker run --rm -p 5050:5050 --name pamw-container pamw-image 
docker run --rm -p 5050:5050 --name pamw-container --mount "type=bind,source=$(pwd)/,target=/app/" pamw-image


#!/bin/sh
# czy da się zastąpić obraz???
# stop container when is running docker ps
# rm if image exists docker images
docker image rm pamw-image
docker build -t pamw-image .
# rm if exists docker ps -a
docker rm pamw-container
docker create -p 5050:5050 --name pamw-container pamw-image
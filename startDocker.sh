#!/bin/sh
# Create docker network
# docker network ls | grep pamw -q || docker network create pamw

# docker image ls | grep pamw-zajecia-main && docker image rm pamw-zajecia-main

# docker build -t pamw-www .
docker image prune -f
docker-compose -f ./docker-compose.yml up --build

# docker run --rm -p 5050:5050 --network pamw --network-alias main --name pamw-container pamw-www 
# docker run --rm -p 5050:5050 --name pamw-container --mount "type=bind,source=$(pwd)/,target=~/" pamw-image


#!/bin/bash
docker-compose --file compose-dev.yml up -d --build
while :
do
    docker-compose --file compose-dev.yml logs --follow crmapi
    sleep 1
done

#!/usr/bin/env bash

version=$(grep "version:" $CONFIG_FILE_PATH | cut -c 10-)
echo "Building version number: " $version
docker push ksula0155/$DOCKER_REPO:$version

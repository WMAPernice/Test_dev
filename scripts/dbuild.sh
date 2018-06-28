#!/usr/bin/env bash

version=$(grep "version:" $CONFIG_FILE_PATH | cut -c 10-)
echo "Building version number: " $version

docker build -f $DOCKER_FILE -t $DOCKER_FULL_REPO:${version} .
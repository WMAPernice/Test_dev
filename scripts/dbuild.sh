#!/usr/bin/env bash

version=$(grep "version:" $CONFIG_FILE_PATH | cut -c 10-)
tag=$(grep "arch: " $CONFIG_FILE_PATH | cut -c 7-)
echo "Building version number: " $version " tag: " $tag

docker build -f $DOCKER_FILE -t $DOCKER_FULL_REPO:${tag}"v"${version} .
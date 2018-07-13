#!/usr/bin/env bash

version=$(grep "version:" $CONFIG_FILE_PATH | cut -c 10-)
version=$(grep "version:" $CONFIG_FILE_PATH | cut -c 10-)
tag=$(grep "arch: " $CONFIG_FILE_PATH | cut -c 7-)
echo "Pushing version number: " $version " tag: " $tag
docker push ksula0155/$DOCKER_REPO:${tag}"v"${version}

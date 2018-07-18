#!/usr/bin/env bash

docker build -f ./docker/Dockerfile.fastai -t wmapernice/ynet_docker_files:$1 . 

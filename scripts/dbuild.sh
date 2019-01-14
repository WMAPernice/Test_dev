#!/usr/bin/env bash

docker build -f ./docker/Dockerfile.mine -t wmapernice/hpa_challenge:$1 . 

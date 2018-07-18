#!/usr/bin/env bash
# test the contents of an image
docker build -f ./docker/Dockerfile.test -t build-context .
docker run --rm -it build-context
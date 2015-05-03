#!/bin/bash

set -x
set -e

sudo docker run --name w3af-collector -v /tmp/collector/:/tmp/ \
                -e "VERSION=${VERSION}" andresriancho/w3af-collector:latest


#!/usr/bin/env bash

set -x
set -e

curl -O https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py

sudo apt-get update
sudo apt-get install -y build-essential python-dev
sudo pip install --upgrade psutil

if ! type "docker" > /dev/null; then
    wget https://get.docker.com/ -O docker.sh
    chmod +x docker.sh
    sudo ./docker.sh
    rm -rf docker.sh
fi

sudo docker pull andresriancho/w3af-collector:latest
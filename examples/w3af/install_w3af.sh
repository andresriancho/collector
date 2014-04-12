#!/bin/bash

set -x

apt-get update --quiet
apt-get install --quiet -y git git-core

git clone --quiet --bare https://github.com/andresriancho/w3af.git
cd w3af

# Checkout the collector-specified version
git checkout $VERSION

# This will generate the installation script
python -c "from w3af.core.controllers.dependency_check.dependency_check import dependency_check;dependency_check()"

/tmp/w3af_dependency_install.sh
#!/bin/bash

set -x
set -e

apt-get install -y --quiet python-dev build-essential python-pip > /dev/null
pip install psutil --upgrade

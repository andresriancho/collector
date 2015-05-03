#!/usr/bin/env bash

set -x
set -e

# https://github.com/andresriancho/w3af/wiki/Profiling-memory-and-CPU-usage
export W3AF_CPU_PROFILING=1
export W3AF_MEMORY_PROFILING=1
export W3AF_CORE_PROFILING=1
export W3AF_THREAD_ACTIVITY=1
export W3AF_PROCESSES=1
export W3AF_PSUTILS=1
export W3AF_PYTRACEMALLOC=1

# Checkout the version we want to test
cd /home/w3af/w3af/
git pull
git checkout ${VERSION}

# Make sure w3af starts and doesn't update
mkdir /home/w3af/.w3af/
cp /tmp/startup.conf /home/w3af/.w3af/

# This will generate the installation script, run it again just in case any new
# dependencies are needed
python -c "from w3af.core.controllers.dependency_check.dependency_check import dependency_check;dependency_check()" || true
sed -i 's/sudo //;' /tmp/w3af_dependency_install.sh
/tmp/w3af_dependency_install.sh

./w3af_console -s /tmp/test-script.w3af

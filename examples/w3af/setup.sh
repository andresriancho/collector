#!/bin/bash

set -x
set -e

mkdir /tmp/collector/

#
#   Make sure that we accept the terms and conditions
#
cat << EOF > /tmp/collector/startup.conf
[STARTUP_CONFIG]
auto-update = false
frequency = D
last-update = 2014-04-10
last-commit = 114fc0cd6f339c1a5c98da8ab88aec5ee6b928fc
accepted-disclaimer = true
EOF


#
#   Create the script
#
cat << EOF > /tmp/collector/test-script.w3af
plugins
output console,text_file
output config text_file
set output_file /tmp/w3af-log-output.txt
set http_output_file /tmp/output-http.txt
set verbose True
back
output config console
set verbose True
back

audit sqli

crawl web_spider
crawl config web_spider
set only_forward True
back

grep path_disclosure

back
target
set target http://www.clarin.com/
back

misc-settings
set max_discovery_time 20
set fuzz_form_files false
back

start

exit
EOF

#
#   w3af run configuration
#
cat << EOF > /tmp/collector/w3af.sh
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

if [ -f /tmp/w3af_dependency_install.sh ]; then
    sed -i 's/sudo //;' /tmp/w3af_dependency_install.sh
    /tmp/w3af_dependency_install.sh
fi

./w3af_console -s /tmp/test-script.w3af
EOF

chmod +x /tmp/collector/w3af.sh
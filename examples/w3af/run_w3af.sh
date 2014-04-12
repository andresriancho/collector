#!/bin/bash

set -x
set -e

#
#   Create the script
#
cat << EOF > /tmp/test-script.w3af
plugins
output console,text_file
output config text_file
set output_file /tmp/output.txt
set http_output_file /tmp/output-http.txt
set verbose True
back
output config console
set verbose False
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

start

exit
EOF

#
#   Make sure that we accept the terms and conditions
#
mkdir ~/.w3af/
cat << EOF > ~/.w3af/startup.conf
[STARTUP_CONFIG]
auto-update = false
frequency = D
last-update = 2014-04-10
last-commit = 114fc0cd6f339c1a5c98da8ab88aec5ee6b928fc
accepted-disclaimer = true
EOF


# https://github.com/andresriancho/w3af/wiki/Profiling-memory-and-CPU-usage
cd w3af
export W3AF_PROFILING=1
./w3af_console -s /tmp/test-script.w3af

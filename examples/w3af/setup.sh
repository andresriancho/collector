#!/bin/bash

set -x
set -e

mkdir /tmp/collector/

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


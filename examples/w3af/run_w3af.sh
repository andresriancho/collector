#!/bin/bash

set -x

cd w3af

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

# https://github.com/andresriancho/w3af/wiki/Profiling-memory-and-CPU-usage
W3AF_PROFILING=1 ./w3af_console -s /tmp/test-script.w3af

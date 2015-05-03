#!/bin/bash

set -x
set -e

grep ' HTTP/1.1' /tmp/collector/output-http.txt | wc -l > /tmp/collector/w3af-request-count.txt


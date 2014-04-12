#!/bin/bash

grep ' HTTP/1.1' /tmp/output-http.txt | wc -l > /tmp/w3af-request-count.txt


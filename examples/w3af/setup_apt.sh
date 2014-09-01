#!/bin/bash

set -x
set -e

echo 'APT::Get::Assume-Yes "true";' > /etc/apt/apt.conf.d/90forceyes
echo 'APT::Get::force-yes "true";' >> /etc/apt/apt.conf.d/90forceyes
echo 'Acquire::http::Pipeline-Depth "0";' >> /etc/apt/apt.conf.d/90-fix-s3

sed 's|us-east-1|us|g;' /etc/apt/sources.list > /tmp/sources.list
mv /tmp/sources.list /etc/apt/sources.list
rm -rf /var/cache/apt/*
apt-get update --quiet > /dev/null
apt-get update --quiet > /dev/null

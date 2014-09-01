#!/bin/bash

set -x
set -e

echo 'APT::Get::Assume-Yes "true";' > /etc/apt/apt.conf.d/90forceyes
echo 'APT::Get::force-yes "true";' >> /etc/apt/apt.conf.d/90forceyes
echo 'Acquire::http::Pipeline-Depth "0";' >> /etc/apt/apt.conf.d/90-fix-s3

sed -i 's/us-east-1/us/g;' /etc/apt/sources.list
rm /var/cache/apt/* -rf
apt-get update --quiet > /dev/null

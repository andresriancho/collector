#!/bin/bash

set -x

echo 'APT::Get::Assume-Yes "true";' > /etc/apt/apt.conf.d/90forceyes
echo 'APT::Get::force-yes "true";' >> /etc/apt/apt.conf.d/90forceyes

apt-get update --quiet > /dev/null

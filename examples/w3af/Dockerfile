# w3af.org

FROM ubuntu:12.04
MAINTAINER Andres Riancho <andres.riancho@gmail.com>

# Initial setup
RUN mkdir /home/w3af
WORKDIR /home/w3af

ENV HOME /home/w3af
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LOGNAME w3af

# Squash errors about "Falling back to ..." during package installation
ENV TERM linux
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN echo 'APT::Get::Assume-Yes "true";' > /etc/apt/apt.conf.d/90forceyes
RUN echo 'APT::Get::force-yes "true";' >> /etc/apt/apt.conf.d/90forceyes
RUN echo 'Acquire::http::Pipeline-Depth "0";' >> /etc/apt/apt.conf.d/90-fix-s3

# Update before installing any package
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y

# Install basic and GUI requirements, python-lxml because it doesn't compile correctly from pip
RUN apt-get install -y build-essential libxslt1-dev libxml2-dev libsqlite3-dev libyaml-dev python-dev \
                       git python-lxml wget curl libssl-dev ca-certificates zlib1g-dev \
                       libssl-dev libbz2-dev libreadline-dev llvm

#
# pytracemalloc installation
#
RUN mkdir /opt/tracemalloc
RUN chown root: /opt/tracemalloc

WORKDIR /tmp/
RUN wget http://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz
RUN wget https://pypi.python.org/packages/source/p/pytracemalloc/pytracemalloc-1.2.tar.gz
RUN tar -xf Python-2.7.8.tgz
RUN tar -xf pytracemalloc-1.2.tar.gz

WORKDIR /tmp/Python-2.7.8
RUN patch -p1 < ../pytracemalloc-1.2/patches/2.7/pep445.patch
RUN ./configure --enable-unicode=ucs4 --prefix=/opt/tracemalloc/py27
RUN make install
RUN mv /usr/bin/python /usr/bin/python.orig
RUN ln -s /opt/tracemalloc/py27/bin/python2.7 /usr/bin/python

RUN curl -O https://bootstrap.pypa.io/get-pip.py
RUN /opt/tracemalloc/py27/bin/python2.7 get-pip.py
RUN ln -s /opt/tracemalloc/py27/bin/pip /usr/local/bin/pip

WORKDIR /tmp/pytracemalloc-1.2
RUN python setup.py install

#
# The new python (at /opt/tracemalloc/py27/bin/python2.7) doesn't have any
# packages installed so I have to install everything from scratch
#
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade distribute

# And the module
RUN pip install pytracemalloc==1.2
# fail fast if tracemalloc is not properly working
RUN python -c 'import tracemalloc'

# Install cython (required by meliae) inside the new python. Installing from the
# ubuntu package doesn't work since that installs it for the "default" python
WORKDIR /tmp/
RUN wget http://cython.org/release/Cython-0.22.tar.gz
RUN tar -zxpvf Cython-0.22.tar.gz
WORKDIR /tmp/Cython-0.22/
RUN python setup.py install

# Install meliae
WORKDIR /tmp/
RUN wget https://launchpad.net/meliae/trunk/0.4/+download/meliae-0.4.0.tar.gz
RUN tar -zxpvf meliae-0.4.0.tar.gz
WORKDIR /tmp/meliae-0.4.0/
RUN python setup.py install
RUN rm -rf /tmp/meliae-0.4.0/

# Install profiling tools
RUN pip install --upgrade yappi
RUN pip install --upgrade psutil
RUN pip freeze

# Get w3af, at least get "one version" here, and in w3af.sh we update it to make sure
# we're testing the latest
WORKDIR /home/w3af/
RUN git clone https://github.com/andresriancho/w3af.git

# This will generate the installation script which we need for installing
# the packages in the new python binary (with pymalloc)
WORKDIR /home/w3af/w3af/
RUN python -c "from w3af.core.controllers.dependency_check.dependency_check import dependency_check;dependency_check()" || true
RUN sed -i 's/sudo //;' /tmp/w3af_dependency_install.sh
RUN /tmp/w3af_dependency_install.sh
RUN rm /tmp/w3af_dependency_install.sh

# Compile the py files into pyc in order to speed-up w3af's start
RUN python -m compileall -q .

# Cleanup to make the image smaller
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
RUN rm -rf /tmp/*
RUN rm -rf /var/tmp/*
RUN rm -rf /tmp/pip-build-root

ADD w3af.sh /home/w3af/w3af/

CMD ["/home/w3af/w3af/w3af.sh"]


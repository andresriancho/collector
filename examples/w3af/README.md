## Goals

 * Tests need to run FAST. The goal is to be able to start measuring performance in the shortest
   time possible, thus we need an AMI which contains most of our pre-requisites installed and ready
   to use.

 * Tests need to be flexible (don't rebuild the whole AMI each time). Thus we use docker images.

## Run step by step

Collector will perform these steps:

 * Start a new EC2 instance with the AMI defined in config.yml
 * Install docker and dependencies in EC2
 * Download the latest docker image (defined in install_dependencies.sh)
 * Run the docker image
 * Retrieve the results

Since the installation of docker in the EC2 instance and the download of the docker image where
tests are run might take considerable time, we want to create a custom AMI and update it only
when there is a major change in test methodology.

## w3af run configuration

Enabling new `w3af` profiling modules or changing the script to be run the performance
test doesn't require changes to the docker image. Just set the desired settings in `setup.sh`

## Improving slow tests

In most cases no changes are required and you just run:

```bash
./collector examples/w3af/config.yml <git-commit>
```

The scan setup has three different phases:
 * Setup the EC2 instance OS to be ready to run docker
 * Download `andresriancho/w3af-collector` to EC2 instance
 * Setup w3af inside docker

If steps 1 or 2 are slow, you'll have to create a new AMI and update your `config.yml` to
point to the latest ami id.

If w3af's setup inside docker is slow, you'll have to build a new `andresriancho/w3af-collector`
in your workstation and then push it to the registry. This will speed-up all `collector`
runs. In some strange cases where your docker image changed drastically, it's recommended
that you re-build the AMI: this will reduce the time of `docker pull`.

## Creating a new AMI

Set the variables:

```bash
export AWS_ACCESS_KEY=
export AWS_SECRET_KEY=
```

And then build:

```bash
# Not required but recommended:
sudo docker build -t andresriancho/w3af-collector .
sudo docker push andresriancho/w3af-collector

# The build itself
~/tools/packer/packer build -var aws_access_key=$AWS_ACCESS_KEY \
                            -var aws_secret_key=$AWS_SECRET_KEY template.packer
```

Update the `config.yml` to point to the new AMI!

## Docker
```
sudo docker build -t andresriancho/w3af-collector .
sudo docker push andresriancho/w3af-collector
```

## Implementation notes

 * `install_dependencies.sh` is used to create the custom AMI and is also run each
 time `./collector` is run. This is a feature, it allows me to run new experiments
 with different EC2 dependencies without creating a new AMI each time.
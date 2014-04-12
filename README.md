## Collector

Collect performance metrics for any software using AWS. Automates the process of running the software on EC2 with the objective of collecting performance metrics for your software. The advantage of using EC2 is that you can run an endless number of variations of your software, without hitting any hardware limitation!

The `collector` helps with the following steps:
 * Start a new EC2 instance
 * Run user specified commands to configure the software to be measured
 * Copy the collected information from the EC2 instance into the `master` host for analysis
 
The collector **DOES NOT** capture any performance metrics. You'll have to setup the performance measuring tools yourself. [There are plans](https://github.com/andresriancho/collector/issues/1) to have some generic performance metric collectors, pull-requests are welcome.

The analysis of the collected results is out of the scope of this project.

While the collector itself is written in `Python` using the amazing `fabric` and `boto` libraries, the user can specify his scripts in any language, as well as test software written in any language.

## Configuration

A complete configuration file looks like this:

```yaml
main:
  output: ~/performance_info/
  performance_results: /tmp/*.cpu
  ec2_instance_size: m1.small
  security_group: collector
  keypair: collector
  ami: ami-709ba735
  user: ubuntu

before_aws_start:
  - before_aws_start.sh # This one is run locally on this workstation

after_aws_start:
  - after_aws_start.pl # Run right after the AWS instance starts, runs remotely
  - local_after_aws_start.py:
      - local: true # Runs locally

setup:
  - install_w3af.rb

run:
  - run_w3af.py:
    - timeout: 15 # In minutes

before_collect:
  - compress_results.py

after_collect: # Both are run, one after the other
  - send_info_to_s3.py
  - remove_tmp.py

before_aws_terminate:
  - collect_cloudwatch_info.py:
     - local: true
  - some_other_command.py
```

All script paths are relative to the configuration file location. The scripts are uploaded using SSH to the user's home directory and run using "sudo".

`timeout: 15` specifies that after 15 minutes the `collect` tool will kill the `run_w3af.py` process and continue with the next phases. This parameter is optional, if not specified the `run_w3af.py` command will run until it finishes by itself.

The files to be downloaded from the EC2 instance to the host running `collect` (ie. CPU and memory usage) is specified using `performance_results: /tmp/*.cpu`. Collect will copy all files matching that wildcard into the `output: ~/performance_info/` directory. See the output section for more information on directory structure inside the `output` directory.

## AWS credentials

`Collector` uses Amazon Web Services to start EC2 instances and run your code. In order to be able to start an instance you'll need to provide AWS credentials in the `~/.boto` file. The format is:

```ini
[Credentials]
aws_access_key_id = ...
aws_secret_access_key = ...
```

## Running

Collector takes two main arguments, the configuration file and a revision:
```console
collect <config.yml> <revision>
```

Collector will set a `VERSION` environment variable for all commands run on the remote EC2 instance. The value of the `VERSION` variable will be equal to the command line argument `revision`. The scripts should use it during `setup` to `git checkout` to the revision to run, for example:

```bash
#!/bin/bash
# Checkout the collector-specified version
git checkout $VERSION
```

## Output

The information collected from the EC2 instances is stored inside the `output`directory specified in the configuration file, `~/performance_info/` in the example. Inside the provided directory `collect` create this directory structure:
 * `revision`
   * `i-e45d5fb5`
   * `i-936361c2`
   * ...
   * `i-ec6a68bd`

Where `revision` was provided in the command line and `i-...` are the EC2 instance IDs where the software was run.

## Analysis

For an example of how the performance output of the `w3af` tool is analyzed, take a look at the [w3af-performance-analysis](https://github.com/andresriancho/w3af-performance-analysis) repository.

## Tips and tricks

 * The performance information might be rather large (memory usage dump usually is 500MB in size), it might be a good idea to run the `collect` command in another EC2 instance to reduce the time it takes to download the information from the newly started EC2 instance to the host running `collect`.

 * You can run the same command several times to gather statistical information about your software and then merge/analyze it.

 * Collect tries to terminate the EC2 instances in all cases (success, errors, exceptions, etc.) but its not a bad idea to check if any EC2 instances are running before you leave the office.
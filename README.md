Collect performance metrics for any software using AWS. Automates the process of running the software on EC2 with the objective of collecting performance metrics for your software. The advantage of using EC2 is that you can run an endless number of variations of your software, without hitting any hardware limitation!

The `collector` helps with the following steps:
 * Start a new EC2 instance
 * Run user specified commands to configure the software to be measured
 * Copy the collected information from the EC2 instance into the `master` host for analysis
 
The analysis of the results is out of the scope of this project.

Since the collected information might be rather large (memory usage usually is 500MB in size), it might be a good idea to run the `collect` command in another EC2 instance: very fast network connection.

The collector **DOES NOT** capture any performance metrics. You'll have to setup the performance measuring tools yourself. [There are plans](https://github.com/andresriancho/collector/issues/1) to have some generic performance metric collectors, pull-requests are welcome.

While the collector itself is written in `Python` using the amazing `fabric` and `boto` libraries, the user can specify his scripts in any language, as well as test software written in any language.

I'm using `yaml` for the configuration format, a complete configuration file would look like this:

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
    - timeout: 60 # In minutes

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

The version of the software to run is set via the command line:
```console
collect <config.yml> <revision>
```

When starting a new instance, and running all the commands, we'll set a `VERSION` environment variable which will equal to the command line argument `revision`. The scripts should use it during `setup` to `git checkout` the revision to analyze, for example:

```python
import os
version = os.environ['VERSION']
git.checkout(version)
```

A user that wants to collect five samples for the same revision can easily run `collect <config.yml> <revision>` on different consoles/via a script.  The information collected from the AWS instances is stored inside the `~/performance_info/` directory. Inside the directory we'll create this directory structure:
 * `revision`
   * Different sub-directories, one for each instance (based on the instance id) were `<revision>` was run

The results to be collected (ie. CPU and memory usage) is specified using `performance_results: /tmp/*.cpu`. The script will copy all files matching that wildcard into the `output: ~/performance_info/` directory.

`timeout: 1h` specifies that after one hour the `collect` tool will kill the `run_w3af.py` process and continue with the next phases. This parameter is optional, if not specified the `run_w3af.py` command will run until it finishes by itself.

For an example of how the performance output of the `w3af` tool is analyzed, take a look at the [w3af-performance-analysis](https://github.com/andresriancho/w3af-performance-analysis) repository.

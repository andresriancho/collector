import logging
import argparse

from fabric.api import settings
from fabric.context_managers import shell_env
from fabric.operations import open_shell

from aws_collector.utils.log import configure_logging
from aws_collector.config.config import Config, check_configuration
from aws_collector.aws.keypair import create_keypair
from aws_collector.utils.collect import collect
from aws_collector.utils.hook_manager import HookManager
from aws_collector.aws.ec2 import (spawn_host, create_security_group,
                                   wait_ssh_ready)
from aws_collector.config.config import (MAIN_CFG, OUTPUT_CFG,
                                         PERFORMANCE_RESULTS_CFG,
                                         EC2_INSTANCE_SIZE_CFG,
                                         SECURITY_GROUP_CFG, KEYPAIR_CFG,
                                         AMI_CFG, USER_CFG,
                                         BEFORE_AWS_START_CFG,
                                         AFTER_AWS_START_CFG, SETUP_CFG,
                                         RUN_CFG, BEFORE_COLLECT_CFG,
                                         AFTER_COLLECT_CFG,
                                         BEFORE_AWS_TERMINATE_CFG)


def main():
    args = parse_args()
    config_file, version = args.config, args.version

    configure_logging(args.debug)

    if not check_configuration(config_file):
        return -9

    conf = Config(config_file)
    conf.parse()

    # Configuration to spawn the EC2 instance
    instance_size = conf.get(MAIN_CFG, EC2_INSTANCE_SIZE_CFG)
    security_group = conf.get(MAIN_CFG, SECURITY_GROUP_CFG)
    keypair = conf.get(MAIN_CFG, KEYPAIR_CFG)
    ami = conf.get(MAIN_CFG, AMI_CFG)
    user = conf.get(MAIN_CFG, USER_CFG)
    # Configuration to collect the data
    performance_results = conf.get(MAIN_CFG, PERFORMANCE_RESULTS_CFG)
    output = conf.get(MAIN_CFG, OUTPUT_CFG)

    # Shortcut
    hook_manager = HookManager(conf, version)
    hook = hook_manager.hook

    hook(BEFORE_AWS_START_CFG)

    try:
        create_keypair(keypair)
        create_security_group(security_group)
    except Exception, e:
        logging.error('Error found during instance setup: "%s"' % e)
        return -1

    try:
        instance = spawn_host(ami, instance_size, keypair, security_group)
    except:
        # logging is done inside spawn_host
        return -2

    try:
        ssh_is_ready = wait_ssh_ready(instance.public_dns_name)
    except KeyboardInterrupt:
        logging.info('Closing...')
        instance.terminate()
        return -3
    except Exception, e:
        logging.error('%s' % e)
        instance.terminate()
        return -3

    if not ssh_is_ready:
        logging.info('SSH is not ready. Terminating instance.')
        instance.terminate()

    host_string = '%s@%s' % (user, instance.public_dns_name)
    key_filename = '%s.pem' % keypair

    with shell_env(VERSION=version):
        with settings(host_string=host_string,
                      key_filename=key_filename,
                      host=instance.public_dns_name,
                      connection_attempts=5,
                      keepalive=1):
            try:
                hook(AFTER_AWS_START_CFG)
                hook(SETUP_CFG)

                try:
                    # We let the user use Ctrl+C to stop the process, this is
                    # good for the cases when there is no timeout and we want
                    # to run "until something happens" (human detects that)
                    hook(RUN_CFG)
                except KeyboardInterrupt:
                    msg = 'Ctrl+C hit, will stop running the remote task'
                    logging.warning(msg)

                # The user's code which will (most likely) kill the software
                # under test
                hook(BEFORE_COLLECT_CFG)

                # My code that gets the files
                collect(conf, performance_results, output, version, instance)

                # Hooks
                hook(AFTER_COLLECT_CFG)
                hook(BEFORE_AWS_TERMINATE_CFG)
            except Exception, e:
                logging.error('A local exception was found: "%s"' % e)
                if args.shell_on_fail:
                    logging.debug('Opening a shell due to user\'s request')
                    open_shell()
                return -4
            except SystemExit:
                logging.error('A remote error was found.')
                if args.shell_on_fail:
                    logging.debug('Opening a shell due to user\'s request')
                    open_shell()
                return -5
            except KeyboardInterrupt:
                logging.info('Closing...')
            finally:
                instance.terminate()

            logging.info('Success.')
            if args.shell_before_terminate:
                logging.debug('Opening a shell due to user\'s request')
                open_shell()

    return 0


def parse_args():
    """
    return: A tuple with config_file, version.
    """
    parser = argparse.ArgumentParser(description='Collect performance statistics')
    parser.add_argument('config', help='Configuration file (ie. config.yml)')
    parser.add_argument('version', help='The version variable to set on the remote EC2 instance')
    parser.add_argument('--debug', action='store_true', help='Print debugging information')
    parser.add_argument('--shell-on-fail', action='store_true', help='Open an interactive shell when a script fails')
    parser.add_argument('--shell-before-terminate', action='store_true', help='Open an interactive shell before EC2 termination')
    args = parser.parse_args()
    return args
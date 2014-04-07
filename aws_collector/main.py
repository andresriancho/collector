import logging

from aws_collector.utils.log import configure_logging
from aws_collector.config.config import Config, check_configuration
from aws_collector.aws.keypair import create_keypair
from aws_collector.utils.collect import collect
from aws_collector.utils.hook_manager import (HookManager,
                                              BEFORE_AWS_START_HOOK,
                                              AFTER_AWS_START_HOOK, SETUP_HOOK,
                                              RUN_HOOK, BEFORE_COLLECT_HOOK,
                                              AFTER_COLLECT_HOOK,
                                              BEFORE_AWS_TERMINATE_HOOK)
from aws_collector.aws.ec2 import (spawn_host, create_security_group,
                                   wait_ssh_ready)


def main():
    configure_logging()

    config_file, version = parse_args()

    if not check_configuration(config_file):
        return -9

    conf = Config(config_file)
    instance_size = conf.get('main', 'ec2_instance_size')
    security_group = conf.get('main', 'security_group')
    keypair = conf.get('main', 'keypair')
    ami = conf.get('main', 'ami')

    # Shortcut
    hook_manager = HookManager(config_file, version)
    hook = hook_manager.hook

    hook(BEFORE_AWS_START_HOOK)

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
        ssh_is_ready = wait_ssh_ready(instance.public_ip)
    except KeyboardInterrupt:
        instance.terminate()
        return -3

    if not ssh_is_ready:
        logging.info('SSH is not ready. Terminating instance.')
        instance.terminate()

    try:
        hook(AFTER_AWS_START_HOOK)
        hook(SETUP_HOOK)
        hook(RUN_HOOK)
        hook(BEFORE_COLLECT_HOOK)

        # My code
        collect()

        # Hooks
        hook(AFTER_COLLECT_HOOK)
        hook(BEFORE_AWS_TERMINATE_HOOK)
    except Exception, e:
        logging.error('An error was found: "%s"' % e)
        return -4
    finally:
        instance.terminate()

    logging.info('Success.')
    return 0


def parse_args():
    """
    return: A tuple with config_file, version.
    """
    raise NotImplementedError
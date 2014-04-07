from __future__ import print_function

import sys
import socket
import logging
import time

from boto.ec2 import EC2Connection
from boto.exception import EC2ResponseError


def spawn_host(ami, instance_size, keypair, security_group):
    """
    Runs run_instances and creates the new ec2 host.
    """
    ec2_conn = EC2Connection()

    logging.debug('All required information gathered, spawning instance in AWS.')


    try:
        run_instances = ec2_conn.run_instances
        reservation = run_instances(ami, key_name=keypair,
                                    instance_type=instance_size,
                                    security_groups=[security_group],)
    except EC2ResponseError, e:
        logging.error('Exception "%s" while starting the instance.' % e.error_message)
        raise

    if not len(reservation.instances) == 1:
        logging.error('More than one instance spawned.')
        raise

    instance = reservation.instances[0]
    logging.info('Spawned instance %s with AMI %s' % (instance.id, ami))

    # Wait for AWS to actually create the instance object
    time.sleep(2)

    ec2_conn.create_tags([instance.id], {"Name": 'collector'})

    while instance.state != u'running':
        logging.debug("Instance state: %s" % instance.state)
        time.sleep(10)
        instance.update()

    return instance


def create_security_group(sg_name):
    conn = EC2Connection()

    for sg in conn.get_all_security_groups():
        if sg.name == sg_name:
            return sg_name

    web = conn.create_security_group(sg_name, 'Allow port 22.')
    web.authorize('tcp', 22, 22, '0.0.0.0/0')

    return sg_name


def wait_ssh_ready(host, tries=40, delay=3, port=22):
    # Wait until the SSH is actually up
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Waiting for SSH at %s to be ready to connect' % host, end='')
    sys.stdout.flush()

    for _ in xrange(tries):
        try:
            s.connect((host, port))
            assert s.recv(3) == 'SSH'
        except KeyboardInterrupt:
            logging.warn('User stopped the wait_ssh_ready loop.')
            raise
        except socket.error:
            time.sleep(delay)
            print('.', end='')
            sys.stdout.flush()
        except AssertionError:
            time.sleep(delay)
            print('!', end='')
            sys.stdout.flush()
        else:
            print() # A new line
            logging.info('SSH is ready to connect')
            return True
    else:
        waited = tries * delay
        logging.error('SSH is not available after %s seconds.' % waited)
        return False
import os
import logging

from fabric.operations import get
from fabric.api import sudo, local, lcd


OUTPUT_FILE = 'collect-output.tar.bz2'


def collect(performance_results, output, version, instance):
    """
    Copy the files from the remote EC2 instance to the local file system for
    later analysis.

    :param performance_results: The expression (/tmp/*.cpu) that output files
                                of the performance test will match, and the ones
                                we need to copy to our host.
    :param output: The local directory where we'll copy the remote files
    """
    version = version.replace('/', '-')
    output = os.path.expanduser(output)
    local_path = os.path.join(output, version, instance.id)

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    local_file_path = os.path.join(local_path, OUTPUT_FILE)

    logging.info('Compressing output')
    sudo('tar -cjpf /tmp/%s %s' % (OUTPUT_FILE, performance_results))

    logging.info('Downloading performance information, might take a while...')
    remote_path = '/tmp/%s' % OUTPUT_FILE
    sudo('ls -lah %s' % remote_path)
    get(remote_path=remote_path, local_path=local_file_path)

    logging.debug('Decompress downloaded data...')
    with lcd(local_path):
        local('tar -jxpvf %s' % OUTPUT_FILE)

    os.unlink(local_file_path)

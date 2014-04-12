import os
import logging

from fabric.operations import get


def collect(performance_results, output, version, instance):
    """
    Copy the files from the remote EC2 instance to the local file system for
    later analysis.

    :param performance_results: The expression (/tmp/*.cpu) that output files
                                of the performance test will match, and the ones
                                we need to copy to our host.
    :param output: The local directory where we'll copy the remote files
    """
    logging.info('Downloading performance information, might take a while...')
    local_path = os.path.join(output, version, instance.id)

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    get(remote_path=performance_results, local_path=local_path)

import os
import logging
import time

from fabric.operations import get
from fabric.api import sudo, local, lcd

from aws_collector.config.config import MAIN_CFG, S3_BUCKET

OUTPUT_FILE_FMT = '%s-%s-collect-output.tar.bz2'
S3_UPLOAD_CMD = 'aws s3 cp --region us-east-1 %s s3://%s/%s'


def collect(conf, performance_results, output, version, instance):
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

    output_file = OUTPUT_FILE_FMT % (int(time.time()), version)
    local_file_path = os.path.join(local_path, output_file)

    logging.info('Compressing output')
    sudo('ls -lah %s' % performance_results)
    sudo('du -sh %s' % performance_results)
    sudo('tar -cjpf /tmp/%s %s' % (output_file, performance_results))

    logging.info('Downloading performance information, might take a while...')
    remote_path = '/tmp/%s' % output_file
    sudo('ls -lah %s' % remote_path)
    get(remote_path=remote_path, local_path=local_file_path)

    logging.debug('Decompress downloaded data...')
    with lcd(local_path):
        local('tar -jxpvf %s' % output_file)

    # Uploading to S3
    try:
        target_bucket = conf.get(MAIN_CFG, S3_BUCKET)
    except KeyError:
        pass
    else:
        logging.debug('Uploading data to S3...')
        s3_upload = S3_UPLOAD_CMD % (local_file_path,
                                     target_bucket,
                                     output_file)
        local(s3_upload)

    os.unlink(local_file_path)

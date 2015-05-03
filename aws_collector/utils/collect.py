import os
import logging
import time
import ConfigParser

from fabric.operations import get
from fabric.api import sudo, local, lcd, cd, shell_env

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
        aws_access, aws_secret = get_aws_credentials()
        if aws_access and aws_secret:
            logging.debug('Uploading data to S3...')
            s3_upload = S3_UPLOAD_CMD % (remote_path,
                                         target_bucket,
                                         output_file)
            with cd('/tmp/'):
                with shell_env(AWS_ACCESS_KEY=aws_access,
                               AWS_SECRET_KEY=aws_secret):
                    sudo(s3_upload)
        else:
            logging.info('Failed to upload data to S3: No AWS credentials'
                         ' were configured in AWS_ACCESS_KEY AWS_SECRET_KEY')

    os.unlink(local_file_path)


def get_aws_credentials():
    """
    :return: AWS_ACCESS_KEY AWS_SECRET_KEY from environment variables or ~/.boto
    """
    if os.environ.get('AWS_ACCESS_KEY') and os.environ.get('AWS_SECRET_KEY'):
        return os.environ.get('AWS_ACCESS_KEY'), os.environ.get('AWS_SECRET_KEY')

    elif os.path.exists(os.path.expanduser('~/.boto')):
        config = ConfigParser.ConfigParser()
        config.read(os.path.expanduser('~/.boto'))
        aws_access = config.get('Credentials', 'aws_access_key_id', None)
        aws_secret = config.get('Credentials', 'aws_secret_access_key', None)
        return aws_access, aws_secret

    return None, None
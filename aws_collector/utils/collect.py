import os
import logging
import time
import ConfigParser

from fabric.operations import get
from fabric.api import sudo, local, lcd, cd, shell_env

from aws_collector.config.config import MAIN_CFG, S3_BUCKET

OUTPUT_FILE_FMT = '%s-%s-collect-output.tar'
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

    output_file = OUTPUT_FILE_FMT % (int(time.time()), version)

    logging.info('Output statistics:')
    sudo('ls -lah %s' % performance_results)
    sudo('du -sh %s' % performance_results)

    logging.info('Compressing output...')
    # performance_results looks like /tmp/collector/w3af-*
    path, file_glob = os.path.split(performance_results)
    with cd(path):
        sudo('tar -cpvf /tmp/%s %s' % (output_file, file_glob))

    # Append config information to tar
    sudo('tar -C /tmp/ -rpvf /tmp/%s config' % output_file)

    # Compress tar file
    sudo('bzip2 -9 /tmp/%s' % output_file)
    output_file = '%s.bz2' % output_file

    remote_path = '/tmp/%s' % output_file
    sudo('ls -lah %s' % remote_path)

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

            # Needed to upload
            sudo('sudo pip install --upgrade awscli')

            with cd('/tmp/'):
                with shell_env(AWS_ACCESS_KEY_ID=aws_access,
                               AWS_SECRET_ACCESS_KEY=aws_secret):
                    sudo(s3_upload)
        else:
            logging.info('Failed to upload data to S3: No AWS credentials'
                         ' were configured in AWS_ACCESS_KEY AWS_SECRET_KEY')

    # Downloading to my workstation
    logging.info('Downloading performance information, might take a while...')

    # Create the output directory if it doesn't exist
    output = os.path.expanduser(output)
    local_path = os.path.join(output, version)

    #
    # Before I stored the output in ~/performance_info/<version>/<instance-id>
    # but that did not help with the analysis phase, since I had to remember
    # those "long" EC2 instance IDs and... it had nothing to do with the
    # analysis itself.
    #
    # Now I just use ~/performance_info/<version>/<unique-incremental-id>
    # where unique-incremental-id is just a number that starts from 0 and
    # increments
    #
    i = -1

    while True:
        i += 1
        potential_output_path = os.path.join(local_path, '%s' % i)

        if not os.path.exists(potential_output_path):
            os.makedirs(potential_output_path)
            local_path = potential_output_path
            break

    # Get the remote file with all the data
    local_file_path = os.path.join(local_path, output_file)
    get(remote_path=remote_path, local_path=local_file_path)

    logging.debug('Decompress downloaded data...')
    with lcd(local_path):
        local('tar -jxpvf %s' % output_file)

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
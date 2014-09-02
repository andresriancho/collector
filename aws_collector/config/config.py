import logging
import yaml
import os

from yaml import load
from yaml import CLoader as Loader

# Main configuration
MAIN_CFG = 'main'
OUTPUT_CFG = 'output'
PERFORMANCE_RESULTS_CFG = 'performance_results'
EC2_INSTANCE_SIZE_CFG = 'ec2_instance_size'
SECURITY_GROUP_CFG = 'security_group'
KEYPAIR_CFG = 'keypair'
AMI_CFG = 'ami'
USER_CFG = 'user'
S3_BUCKET = 'S3'

# Hooks
SETUP_CFG = 'setup'
RUN_CFG = 'run'
BEFORE_AWS_START_CFG = 'before_aws_start'
AFTER_AWS_START_CFG = 'after_aws_start'
BEFORE_COLLECT_CFG = 'before_collect'
AFTER_COLLECT_CFG = 'after_collect'
BEFORE_AWS_TERMINATE_CFG = 'before_aws_terminate'

REQUIRED_CONFIGS = [(MAIN_CFG, OUTPUT_CFG),
                    (MAIN_CFG, PERFORMANCE_RESULTS_CFG),
                    (MAIN_CFG, EC2_INSTANCE_SIZE_CFG),
                    (MAIN_CFG, SECURITY_GROUP_CFG),
                    (MAIN_CFG, KEYPAIR_CFG),
                    (MAIN_CFG, AMI_CFG),
                    (MAIN_CFG, USER_CFG),
                    (SETUP_CFG,),
                    (RUN_CFG,)]

HOOKS = {SETUP_CFG, RUN_CFG, BEFORE_AWS_START_CFG, AFTER_AWS_START_CFG,
         BEFORE_COLLECT_CFG, AFTER_COLLECT_CFG, BEFORE_AWS_TERMINATE_CFG}


class Config(object):
    """
    Parser for the configuration file.
    """
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_path = os.path.dirname(config_file)
        self.hooks = []
        self.config = None

    def parse(self):
        """
        Uses REQUIRED_CONFIGS to make sure all the required parameter names
        are correctly set.

        :return: A tuple with
                    - True/False depending on the result of the check
                    - A list with all the errors

        """
        error_list = []
        success = True

        #
        # Check for syntax errors
        #
        try:
            self.config = load(file(self.config_file), Loader=Loader)
        except yaml.scanner.ScannerError, yse:
            error_list.append('Incorrect syntax in config file: %s' % yse)
            return False, error_list

        #
        # Check that the required sections are all there
        #
        for req_keys in REQUIRED_CONFIGS:
            try:
                self.get(*req_keys)
            except KeyError:
                error_list.append(self._format_required_error(req_keys))

        if error_list:
            return False, error_list

        #
        # Check the values provided in the configuration file
        #
        # Does the output directory exist?
        output_dir = os.path.expanduser(self.get(MAIN_CFG, OUTPUT_CFG))
        if not os.path.isdir(output_dir):
            error_list.append('Output directory %s does not exist.' % output_dir)

        # Do the scripts exist, and are marked as executable?
        self._parse_hooks()

        for hook_name, script, params in self.hooks:

            script_path = os.path.join(self.config_path, script)

            if not os.path.exists(script_path):
                error_list.append('%s does not exist.' % script_path)
                success = False
            elif not os.access(script_path, os.X_OK):
                error_list.append('%s is not executable.' % script_path)
                success = False

        return success, error_list

    def _parse_hooks(self):
        """
        Parse the hooks from the configuration file
        """
        for hook_name in HOOKS:
            try:
                hook_info = self.get(hook_name)
            except KeyError:
                logging.debug('No %s hook provided' % hook_name)
                continue

            # At this point the hook_info looks like this:
            #   ['compress_results.py']
            #   ['send_info_to_s3.py', 'remove_tmp.py']
            #   [{'collect_cloudwatch_info.py': ['local']}, 'some_other_command.py']
            for script_info in hook_info:
                if isinstance(script_info, basestring):
                    script = script_info
                    params = {}
                else:
                    script = script_info.keys()[0]
                    params = script_info[script][0]

                self._append_hook(hook_name, script, params)

    def _append_hook(self, hook_name, script, params):
        logging.debug('Adding hook %s: %s %s' % (hook_name, script, params))

        self.hooks.append((hook_name, script, params))

    def _format_required_error(self, req_keys):
        """
        :return: A string representing the error of a missing key
        """
        fmt = '%s is a required section of the configuration file.'
        data = '/'.join(req_keys)
        return fmt % data

    def get(self, *args):
        """
        :return: A configuration value, based on a path provided as param.
        """
        return self._internal_get(self.config, args)

    def _internal_get(self, config, path):
        if not len(path):
            raise ValueError('Invalid call to get()')
        elif not path[0] in config:
            raise KeyError('%s not found in %s' % (path[0], config))
        elif len(path) == 1:
            return config[path[0]]
        else:
            return self._internal_get(config[path[0]], path[1:])


def check_configuration(config_file):
    c = Config(config_file)

    success, error_list = c.parse()
    if not success:
        for error in error_list:
            logging.error(error)

    return success

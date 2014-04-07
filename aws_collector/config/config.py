import logging
import yaml


MAIN_CFG = 'main'
OUTPUT_CFG = 'output'
PERFORMANCE_RESULTS_CFG = 'performance_results'
EC2_INSTANCE_SIZE_CFG = 'ec2_instance_size'
SECURITY_GROUP_CFG = 'security_group'
KEYPAIR_CFG = 'keypair'
AMI_CFG = 'ami'
USER_CFG = 'user'
SETUP_CFG = 'setup'
RUN_CFG = 'run'


REQUIRED_CONFIGS = [(MAIN_CFG, OUTPUT_CFG),
                    (MAIN_CFG, PERFORMANCE_RESULTS_CFG),
                    (MAIN_CFG, EC2_INSTANCE_SIZE_CFG),
                    (MAIN_CFG, SECURITY_GROUP_CFG),
                    (MAIN_CFG, KEYPAIR_CFG),
                    (MAIN_CFG, AMI_CFG),
                    (MAIN_CFG, USER_CFG),
                    (SETUP_CFG,),
                    (RUN_CFG,)]


class Config(object):
    """
    Parser for the configuration file.
    """
    def __init__(self, config_file):
        self.config_file = config_file

    def check(self):
        """
        Uses REQUIRED_CONFIGS to make sure all the required parameter names
        are correctly set.

        :return: A tuple with
                    - True/False depending on the result of the check
                    - A list with all the errors

        """
        success = True
        error_list = []

        # TODO: Check that all required configuration settings are there
        # TODO: Check that the output directory exists
        # TODO: Check that all referenced scripts are executable
        raise NotImplementedError

        return success, error_list

    def get(self, *args):
        """
        :return: A configuration value, based on a path provided as param.
        """
        raise NotImplementedError


def check_configuration(config_file):
    c = Config(config_file)

    success, error_list = c.check()
    if not success:
        for error in error_list:
            logging.error(error)

    return success

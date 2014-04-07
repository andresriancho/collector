import logging
import yaml


REQUIRED_CONFIGS = [('main', 'output'),
                    ('main', 'performance_results'),
                    ('main', 'ec2_instance_size'),
                    ('main', 'security_group'),
                    ('main', 'keypair'),
                    ('main', 'ami'),
                    ('setup',),
                    ('run',)]


class Config(object):
    """
    Parser for the configuration file.
    """
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



        return success, error_list


def check_configuration():
    c = Config()

    success, error_list = c.check()
    if not success:
        for error in error_list:
            logging.error(error)

    return success

import os
import logging

from fabric.operations import put
from fabric.api import run, sudo, settings
from fabric.exceptions import CommandTimeout

from aws_collector.config.config import BEFORE_AWS_START_CFG, MAIN_CFG, USER_CFG

LOCAL = 'local'
TIMEOUT = 'timeout'
LOCAL_HOOKS = {BEFORE_AWS_START_CFG}


class HookManager(object):
    def __init__(self, conf, version):
        """
        :param conf: A configuration object which basically wraps the config.yml
        :param version: The version that we want to test (cli argument)
        """
        self.conf = conf
        self.version = version

    def hook(self, run_hook_name):
        # self.hooks.append((hook_name, script, params))
        for configured_hook_name, script, params in self.conf.hooks:
            if run_hook_name == configured_hook_name:
                self._run_hook(configured_hook_name, script, params)

    def _run_hook(self, configured_hook_name, script, params):
        """
        Run the configured hook

        :param configured_hook_name: The name of the hook we're running
        :param script: The script to run
        :param params: A dict with the parameters
        """
        log_args = (configured_hook_name, script, params)
        logging.info('[%s] %s with params %r' % log_args)

        if self._should_run_locally(configured_hook_name, script, params):
            self._run_local_hook(configured_hook_name, script, params)
        else:
            self._copy_script(script)
            self._run_remote_script(configured_hook_name, script, params)

    def _should_run_locally(self, configured_hook_name, script, params):
        """
        :return: True if we want to run this script in this host
        """
        if configured_hook_name == LOCAL_HOOKS:
            return True

        return params.get(LOCAL, False)

    def _run_local_hook(self, configured_hook_name, script, params):
        """
        :return: None, all the important output is shown on stdout
        """
        command = os.path.join(self.conf.config_path, script)
        run(command, shell=True)

    def _copy_script(self, script):
        """
        Copy the script to the remote host

        :param script: The script path
        """
        logging.debug('Copying %s to the remote server...' % script)

        local_path = os.path.join(self.conf.config_path, script)
        remote_path = '/home/%s' % self.conf.get(MAIN_CFG, USER_CFG)
        put(local_path, remote_path, mirror_local_mode=True)

    def _run_remote_script(self, configured_hook_name, script, params):
        """
        Run a script remotely
        """
        command = '/home/%s/%s' % (self.conf.get(MAIN_CFG, USER_CFG), script)
        timeout = self._get_command_timeout(params)
        warn_only = params.get('warn_only', False)

        with settings(warn_only=warn_only):
            try:
                result = sudo(command, shell=True, timeout=timeout)
            except CommandTimeout:
                logging.info('Configured timeout reached')
            else:
                if result.failed:
                    msg = 'The remote command returned exit code != 0,'\
                          ' execution will continue but results may be'\
                          ' incomplete/broken.'
                    logging.warn(msg)

    def _get_command_timeout(self, params):
        """
        :return: The timeout for the command being run, in seconds. Converts the
                 timeout from the config which is in minutes.
        """
        timeout = params.get(TIMEOUT, None)

        if timeout is not None:
            timeout *= 60

        return timeout
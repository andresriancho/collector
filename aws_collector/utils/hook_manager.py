BEFORE_AWS_START_HOOK = 'before_aws_start'
AFTER_AWS_START_HOOK = 'after_aws_start'
SETUP_HOOK = 'setup'
RUN_HOOK = 'run'
BEFORE_COLLECT_HOOK = 'before_collect'
AFTER_COLLECT_HOOK = 'after_collect'
BEFORE_AWS_TERMINATE_HOOK = 'before_aws_terminate'


def noop():
    pass


class HookManager(object):
    def __init__(self, config_file, version):
        self.config_file = config_file
        self.version = version

        self.hook_dict = self.configure_hooks()

    def hook(self, hook_name):
        self.hook_dict.get(hook_name)()

    def configure_hooks(self):
        """
        Read the configuration file and return a dictionary with all the hooks,
        containing the hook name as key and the function to run for that hook as
        value.
        """
        raise NotImplementedError
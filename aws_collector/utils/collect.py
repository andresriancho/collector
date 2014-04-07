def collect(performance_results, output):
    """
    Copy the files from the remote EC2 instance to the local file system for
    later analysis.

    :param performance_results: The expression (/tmp/*.cpu) that output files
                                of the performance test will match, and the ones
                                we need to copy to our host.
    :param output: The local directory where we'll copy the remote files
    """

    # TODO: Raise an exception if no files match the remote expression
    raise NotImplementedError

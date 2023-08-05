"""Test an extraction plugin using the provided test framework."""
import argparse
import sys
from typing import Type

from hansken_extraction_plugin.runtime.reflection_util import get_plugin_class
from hansken_extraction_plugin.test_framework.validator import ByClassTestPluginRunner, DockerTestPluginRunner,\
    FlitsTestRunner, log_context, PluginValidator, RemotelyStartedTestPluginRunner


def _test_validate_standalone(plugin_class: Type, input_path, result_path, regenerate, verbose):
    with log_context():
        # setup test
        test_runner = FlitsTestRunner(input_path, result_path, regenerate, verbose)
        standalone_runner = ByClassTestPluginRunner(plugin_class)
        validator = PluginValidator(test_runner, standalone_runner)
        validator.validate_plugin()


def _test_validate_manual(hostname, port, input_path, result_path, regenerate, verbose):
    with log_context():
        test_runner = FlitsTestRunner(input_path, result_path, regenerate, verbose)
        manual_runner = RemotelyStartedTestPluginRunner(hostname, port)
        validator = PluginValidator(test_runner, manual_runner)
        validator.validate_plugin()


def _test_validate_docker(docker_repository, input_path, result_path, regenerate, verbose):
    with log_context():
        test_runner = FlitsTestRunner(input_path, result_path, regenerate, verbose)
        standalone_runner = DockerTestPluginRunner(docker_repository)
        validator = PluginValidator(test_runner, standalone_runner)
        validator.validate_plugin()


def main():
    """Run tests for a provided extraction plugin."""
    parser = argparse.ArgumentParser(prog='test_plugin',
                                     usage='%(prog)s [options]',
                                     description='A script to run three types of tests on your plugin.')

    parser.add_argument('-s', '--standalone', metavar='PLUGIN_FILE_PATH',
                        help='Run the FLITS test against the plugin served locally.')
    parser.add_argument('-m', '--manual', nargs=2, metavar=('SERVER', 'PORT'),
                        help='Run the FLITS test against the plugin running on the server SERVER with port PORT.\
                        The plugin is expected to be already running (use command serve_plugin).')
    parser.add_argument('-d', '--docker', metavar='DOCKER_IMAGE',
                        help='Run the FLITS test against the plugin running in a docker container.')
    parser.add_argument('-i', '--input', default='testdata/input', help='PATH to the input files.')
    parser.add_argument('-r', '--result', default='testdata/result', help='PATH to the result files.')
    parser.add_argument('-reg', '--regenerate', action='store_true', help='Regenerate test results.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')

    args = parser.parse_args()

    test_standalone = args.standalone
    test_manual = args.manual
    test_docker = args.docker

    input_path = args.input
    result_path = args.result
    regenerate = args.regenerate
    verbose = args.verbose

    if not test_standalone and not test_docker and not test_manual:  # and not test_manual:
        print('No tests were run. Try "test_plugin -h" to show all options for running tests.')
        sys.exit(2)

    if test_standalone:
        plugin_class = get_plugin_class(test_standalone)
        _test_validate_standalone(plugin_class, input_path, result_path, regenerate, verbose)
    if test_docker:
        _test_validate_docker(test_docker, input_path, result_path, regenerate, verbose)
    if test_manual:
        _test_validate_manual(test_manual[0], test_manual[1], input_path, result_path, regenerate, verbose)

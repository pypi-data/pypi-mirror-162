"""Contains a cmd entry point to create a plugin docker image with plugin info labels."""
import argparse
import os
from shlex import join
import subprocess  # nosec
import sys

from logbook import Logger  # type: ignore

from hansken_extraction_plugin.framework import GRPC_API_VERSION
from hansken_extraction_plugin.runtime.reflection_util import get_plugin_class

log = Logger(__name__)


def _build(plugin_class, docker_file, name):
    plugin_info = plugin_class().plugin_info()

    plugin_id = str(plugin_info.id)
    labels = {
        'org.hansken.plugin-info.id': plugin_id,
        'org.hansken.plugin-info.id-domain': plugin_info.id.domain,
        'org.hansken.plugin-info.id-category': plugin_info.id.category,
        'org.hansken.plugin-info.id-name': plugin_info.id.name,
        'org.hansken.plugin-info.version': plugin_info.version,
        'org.hansken.plugin-info.api-version': GRPC_API_VERSION,
        'org.hansken.plugin-info.description': plugin_info.description,
        'org.hansken.plugin-info.webpage': plugin_info.webpage_url,
        'org.hansken.plugin-info.deferred-iterations': plugin_info.deferred_iterations,
        'org.hansken.plugin-info.matcher': plugin_info.matcher,
        'org.hansken.plugin-info.license': plugin_info.license,
        'org.hansken.plugin-info.maturity-level': plugin_info.maturity.name,
        'org.hansken.plugin-info.author-name': plugin_info.author.name,
        'org.hansken.plugin-info.author-organisation': plugin_info.author.organisation,
        'org.hansken.plugin-info.author-email': plugin_info.author.email,
    }

    if plugin_info.resources:
        labels['org.hansken.plugin-info.resource-max-cpu'] = plugin_info.resources.maximum_cpu
        labels['org.hansken.plugin-info.resource-max-mem'] = plugin_info.resources.maximum_memory

    if not name:
        name = f'extraction-plugins/{plugin_id}'

    command = ['docker', 'build',
               docker_file,
               '-t', f'{name}:{plugin_info.version}'.lower(),
               '-t', f'{name}:latest'.lower()]

    for (label, value) in labels.items():
        command.append('--label')
        command.append(f'{label}={value}')

    log.info(f' -> Invoking Docker build with command: {join(command)}')
    os.environ['SYSTEMD_COLORS'] = '1'

    # execute the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  # nosec

    # print the output of the command
    for c in iter(lambda: process.stdout.read(1), b''):
        sys.stdout.buffer.write(c)
        sys.stdout.flush()
    process.wait()

    if process.returncode != 0:
        raise RuntimeError(f' -> DOCKER BUILD FAILED (see logs above this line for more details)\n'
                           f'    command was: {join(command)}')
    else:
        log.info(' -> Docker build finished')
    return process.returncode


def _parse_args(args):
    parser = argparse.ArgumentParser(prog='build_plugin',
                                     usage='%(prog)s PLUGIN_FILE DOCKER_FILE_DIRECTORY [-n DOCKER_IMAGE_NAME] '
                                           '(Use -h for help)',
                                     description='Build an Extraction Plugin docker image according to provided '
                                                 'arguments.')
    parser.add_argument('plugin_file', metavar='PLUGIN_FILE', help='Path to the python file of the plugin.')
    parser.add_argument('docker_file', metavar='DOCKER_FILE_DIRECTORY', help='Path to the directory containing the '
                                                                             'Dockerfile of the plugin.')
    parser.add_argument('-n', '--name', metavar='DOCKER_IMAGE_NAME', help='Name of the docker image without tag '
                                                                          '(optional).')
    return parser.parse_args(args)


def _build_using_plugin_file(plugin_file, docker_file, name):
    plugin_class = get_plugin_class(plugin_file)

    if plugin_class is not None:
        try:
            _build(plugin_class, docker_file, name)
        except RuntimeError as e:
            log.error(str(e))
    else:
        log.error(f'No Extraction Plugin class found in {plugin_file}')


def main():
    """Build an Extraction Plugin docker image according to provided arguments."""
    arguments = _parse_args(sys.argv[1:])
    _build_using_plugin_file(arguments.plugin_file, arguments.docker_file, arguments.name)

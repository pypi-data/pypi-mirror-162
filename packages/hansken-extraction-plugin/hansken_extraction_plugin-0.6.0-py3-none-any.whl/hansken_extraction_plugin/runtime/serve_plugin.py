"""Contains a cmd entry point to serve a plugin."""
import argparse
import os
import signal
import sys
import threading
import time
from typing import Type

from logbook import Logger, StreamHandler  # type: ignore

from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin
from hansken_extraction_plugin.runtime.extraction_plugin_server import serve_indefinitely
from hansken_extraction_plugin.runtime.reflection_util import get_plugin_class

log = Logger(__name__)


def hardkill():
    """
    Fully kill the current application.

    This is useful in cases where all other ways to stop the application fails.
    """
    time.sleep(.2)
    log.error('Failed to stop process, taking drastic measures now, goodbye cruel world!')
    try:
        os._exit(1)
    finally:
        os.kill(os.getpid(), signal.SIGKILL)


def serve(extraction_plugin_class: Type[BaseExtractionPlugin], port=8999) -> None:
    """
    Initialize and serve the provided plugin on provided port.

    :param extraction_plugin_class: plugin to be served
    :param port: port plugin can be reached
    """
    log.info(f'Serving chat plugin on port {port}...')
    serve_indefinitely(extraction_plugin_class, f'[::]:{port}')

    # we are leaving the main thread, start a small thread to kill the entire
    # application if we don't exit gracefully when some other threads are
    # blocking the application to stop
    threading.Thread(target=hardkill, daemon=True).start()


def main():
    """Run an Extraction Plugin according to provided arguments."""
    parser = argparse.ArgumentParser(prog='serve_plugin',
                                     usage='%(prog)s FILE PORT (Use -h for help)',
                                     description='Run an Extraction Plugin according to provided arguments.')

    parser.add_argument('file', metavar='FILE', help='Path of the python file of the plugin to be served.')
    parser.add_argument('port', metavar='PORT', help='Port where plugin is served on.', type=int)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Verbosity level. -v = NOTICE, -vv = INFO, -vvv = DEBUG. Default is WARNING.')

    arguments = parser.parse_args()

    verbose = arguments.verbose
    verbose = min(max(0, verbose), 3)
    loglevel = ['WARNING', 'NOTICE', 'INFO', 'DEBUG'][verbose]
    log_handler = StreamHandler(sys.stdout, bubble=True, level=loglevel)

    with log_handler.applicationbound():
        plugin_file = arguments.file
        port = arguments.port

        if (not plugin_file.endswith('.py')):
            log.error('Not a python file: ' + plugin_file)
            sys.exit(1)

        plugin_class = get_plugin_class(plugin_file)
        if plugin_class is not None:
            serve(plugin_class, port)
        else:
            log.error('No Extraction Plugin class found in ' + plugin_file)
            sys.exit(1)

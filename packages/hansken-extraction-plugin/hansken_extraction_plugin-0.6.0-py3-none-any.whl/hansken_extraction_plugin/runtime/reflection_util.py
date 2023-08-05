"""Helper methods to find out more about the class of a plugin."""
import importlib.util
import inspect
import sys
from typing import Optional, Type

from logbook import Logger  # type: ignore

from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin

log = Logger(__name__)


def is_abstract(cls: Type) -> bool:
    """
    Verify if provided class is abstract.

    An abstract class has a __abstractmethods__ property containing a set of
    abstract method names. See https://www.python.org/dev/peps/pep-3119/.

    :param cls: class that may be abstract
    :returns: true if class is abstract
    """
    if hasattr(cls, '__abstractmethods__'):
        return len(cls.__abstractmethods__) > 0
    return False


def get_plugin_class(plugin_file) -> Optional[Type]:
    """
    Retrieve the parent class of a plugin contained in the provided file.

    :param plugin_file: path of the python source file that should contain a Extraction Plugin class definition
    :returns: the first class that is found in the plugin_file that is a subclass of ExtractionPlugin or
              MetaExtractionPlugin.
    """
    try:
        # Import the plugin_file into code
        spec = importlib.util.spec_from_file_location('plugin_module', plugin_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules['plugin_module'] = module
        spec.loader.exec_module(module)  # type: ignore

        # Loop over all classes found in the pluginFile. The first class that is a subclass of ExtractionPlugin
        # or MetaExtractionPlugin will be the pluginClass that is served.
        plugin_class = None
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, BaseExtractionPlugin) and not is_abstract(cls):
                plugin_class = cls
                log.info(f'Plugin class found: {plugin_class}')
                break

        return plugin_class
    except FileNotFoundError:
        log.error(f'Specified file not found: {plugin_file}')
    return None

"""
This module contains the different types of Extraction Plugins.

The types of Extraction Plugins differ in their process functions.
"""
from abc import ABC, abstractmethod

from hansken_extraction_plugin.api.data_context import DataContext
from hansken_extraction_plugin.api.extraction_trace import ExtractionTrace, MetaExtractionTrace
from hansken_extraction_plugin.api.plugin_info import PluginInfo
from hansken_extraction_plugin.api.trace_searcher import TraceSearcher


class BaseExtractionPlugin(ABC):
    """All Extraction Plugins are derived from this class."""

    @abstractmethod
    def plugin_info(self) -> PluginInfo:
        """Return information about this extraction plugin."""


class ExtractionPlugin(BaseExtractionPlugin):
    """Default extraction plugin, that processes a trace and one of its datastreams."""

    @abstractmethod
    def process(self, trace: ExtractionTrace, data_context: DataContext):
        """
        Process a given trace.

        This method is called for every trace that is processed by this tool.

        :param trace: Trace that is being processed
        :param data_context: Data data_context describing the data stream that is being processed
        """


class MetaExtractionPlugin(BaseExtractionPlugin):
    """Extraction Plugin that processes a trace only with its metadata, without processing its data."""

    @abstractmethod
    def process(self, trace: MetaExtractionTrace):
        """
        Process a given trace.

        This method is called for every trace that is processed by this tool.

        :param trace: Trace that is being processed
        """


class DeferredExtractionPlugin(BaseExtractionPlugin):
    """
    Extraction Plugin that can be run at a different extraction stage.

    This type of plugin also allows accessing other traces using the searcher.
    """

    @abstractmethod
    def process(self, trace: ExtractionTrace, data_context: DataContext, searcher: TraceSearcher):
        """
        Process a given trace.

        This method is called for every trace that is processed by this tool.

        :param trace: Trace that is being processed
        :param data_context: Data data_context describing the data stream that is being processed
        :param searcher: TraceSearcher that can be used to obtain more traces
        """

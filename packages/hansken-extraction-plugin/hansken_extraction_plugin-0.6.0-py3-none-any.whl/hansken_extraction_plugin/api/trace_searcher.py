"""This module contains the definition of a trace searcher."""
from abc import abstractmethod

from hansken_extraction_plugin.api.search_result import SearchResult


class TraceSearcher:
    """This class can be used to search for traces, using the search method."""

    @abstractmethod
    def search(self, query: str, count: int) -> SearchResult:
        """
        Search for indexed traces in Hansken using provided query returning at most count results.

        :param query: HQL-query used for searching
        :param count: Maximum number of traces to return
        :return: SearchResult containing found traces
        """

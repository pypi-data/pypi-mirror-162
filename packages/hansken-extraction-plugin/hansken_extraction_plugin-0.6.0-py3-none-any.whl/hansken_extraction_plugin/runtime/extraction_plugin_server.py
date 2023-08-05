"""Implementation of the api using generated gRPC code."""
from concurrent import futures
from contextlib import contextmanager
from dataclasses import dataclass, field
from io import BufferedReader
from queue import Queue
from signal import SIGINT, signal, SIGTERM
import threading
from typing import Any, Callable, cast, Dict, Generator, Iterator, List, Mapping, Optional, Sequence, Set, Tuple, \
    Type, Union

from google.protobuf.any_pb2 import Any as GrpcAny
import grpc
from logbook import Logger  # type: ignore

from hansken_extraction_plugin import __version__ as api_version
from hansken_extraction_plugin.api.data_context import DataContext
from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin, DeferredExtractionPlugin, \
    ExtractionPlugin, MetaExtractionPlugin
from hansken_extraction_plugin.api.extraction_trace import ExtractionTrace, ExtractionTraceBuilder, SearchTrace, \
    Tracelet
from hansken_extraction_plugin.api.search_result import SearchResult
from hansken_extraction_plugin.api.trace_searcher import TraceSearcher
from hansken_extraction_plugin.api.transformation import Transformation
from hansken_extraction_plugin.framework.DataMessages_pb2 import RpcPluginInfo, RpcRandomAccessDataMeta, \
    RpcSearchTrace, RpcTrace
from hansken_extraction_plugin.framework.ExtractionPluginService_pb2_grpc import \
    add_ExtractionPluginServiceServicer_to_server, ExtractionPluginServiceServicer
from hansken_extraction_plugin.framework.Health_pb2 import HealthCheckResponse
from hansken_extraction_plugin.framework.Health_pb2_grpc import add_HealthServicer_to_server, HealthServicer
from hansken_extraction_plugin.framework.RpcCallMessages_pb2 import RpcFinish, RpcRead, RpcSearchResult, RpcStart
from hansken_extraction_plugin.runtime import pack, unpack
from hansken_extraction_plugin.runtime.common import validate_update_arguments
from hansken_extraction_plugin.runtime.constants import MAX_CHUNK_SIZE, MAX_MESSAGE_SIZE
from hansken_extraction_plugin.runtime.grpc_raw_io import _GrpcRawIO

log = Logger(__name__)


class GrpcExtractionTraceBuilder(ExtractionTraceBuilder):
    """
    Helper class that implements a trace builder that was exchanged with the gRPC protocol.

    This trace will only be created in Hansken when `.build` is called. No gRPC message is sent before `.build` is
    called
    """

    def __init__(self, grpc_handler: 'ProcessHandler', trace_id: str, name: Optional[str]):
        """
        Initialize a builder.

        :param grpc_handler: ProcessHandler that handles gRPC requests.
        :param trace_id: string representing the internal id of this trace.
        :param name: name of this trace. Can be added later using `.update`, but a name is required before building a
                     trace.
        """
        self._grpc_handler = grpc_handler
        self._trace_id = trace_id
        self._next_child_id = 0
        self._types: Set[str] = set()
        self._properties: Dict[str, object] = {}
        self._tracelets: List[Tracelet] = []
        self._transformations: Dict[str, List[Transformation]] = {}
        self._has_been_built = False
        self._datas: Dict[str, bytes] = {}

        if name:
            self.update('name', name)

    def get(self, key: str, default=None):
        """Retrieve property corresponding to a provided key from this trace."""
        return self._properties[key] if key in self._properties else default

    def update(self, key_or_updates=None, value=None, data=None) -> ExtractionTraceBuilder:
        """Override :meth: `ExtractionTraceBuilder.update`."""
        if key_or_updates is not None:
            types, properties = _extract_types_and_properties(self._properties, key_or_updates, value)
            self._types.update(types)
            self._properties.update(properties)
        if data is not None:
            for data_type in data:
                if data_type in self._datas:
                    raise RuntimeError(f'data with type {data_type} already exists on this trace')
            self._datas = data
        return self

    def add_tracelet(self,
                     tracelet: Union[Tracelet, str],
                     value: Optional[Mapping[str, Any]] = None) -> 'ExtractionTraceBuilder':
        """Override :meth: `ExtractionTraceBuilder.add_tracelet`."""
        if isinstance(tracelet, Tracelet) and not value:
            self._tracelets.append(tracelet)
        elif isinstance(tracelet, str) and value:
            self._tracelets.append(Tracelet(tracelet, value))
        else:
            raise TypeError('invalid arguments for adding tracelet, '
                            'need either tracelet type and value or Tracelet object')
        return self

    def add_transformation(self, data_type: str, transformation: Transformation) -> 'ExtractionTraceBuilder':
        """Override :meth: `ExtractionTraceBuilder.add_transformation`."""
        if not data_type:
            raise ValueError('data_type is required')
        if transformation is None:
            raise ValueError('transformation is required')
        self._transformations.setdefault(data_type, []).append(transformation)
        return self

    def child_builder(self, name: str = None) -> ExtractionTraceBuilder:
        """Override :meth: `ExtractionTraceBuilder.child_builder`."""
        if not self._has_been_built:
            raise RuntimeError('parent trace has not been built before creating a child')
        return GrpcExtractionTraceBuilder(self._grpc_handler, self._get_next_child_id(), name)

    def build(self) -> str:
        """Override :meth: `ExtractionTraceBuilder.build`."""
        self._grpc_handler.begin_child(self._trace_id, self.get('name'))
        self._flush()
        self._grpc_handler.write_datas(self._trace_id, self._datas)
        self._grpc_handler.finish_child(self._trace_id)
        self._has_been_built = True
        return self._trace_id

    def _get_next_child_id(self):
        """
        Compute the next id of a child of this trace.

        Note that this may not be the same id the remote uses, as this is computed after the trace is build.
        """
        next_id = self._trace_id + '-' + str(self._next_child_id)
        self._next_child_id = self._next_child_id + 1
        return next_id

    def _flush(self):
        log.debug('Flushing trace builder {}', self._trace_id)
        # remove name property as it was already given through self._grpc_handler#begin_child
        # and the properties are cleared anyway (and flush is only called when the child is built)
        del self._properties['name']
        self._grpc_handler.enrich_trace(self._trace_id,
                                        self._types,
                                        self._properties,
                                        self._tracelets,
                                        self._transformations)
        self._types.clear()
        self._properties.clear()


@dataclass(frozen=True)
class GrpcDataContext(DataContext):
    """Class that extends a DataContext that also could hold the first bytes of the data it represents."""

    first_bytes: bytes = field(compare=False)
    """
    The first bytes of the data stream currently being processed.
    This could be `None` or an empty bytes. This does not imply that there is no data, but it means that the client
    did not send data to fill a data cache. Use `data_size` to verify the presence of data.
    """


class GrpcExtractionTrace(ExtractionTrace):
    """Helper class that exposes a trace that was exchanged with the gRPC protocol."""

    def __init__(self, grpc_handler: 'ProcessHandler', trace_id: str, properties: Dict[str, Any],
                 data_context: GrpcDataContext, tracelets: List[Tracelet],
                 transformations: Dict[str, List[Transformation]]):
        """
        Initialize an GrpcExtractionTrace.

        :param grpc_handler: ProcessHandler that can be used to perform gRPC requests.
        :param trace_id: string representing the id of this trace.
        :param properties: key, value mapping of all known properties of this trace.
        :param data_context: data_context used to retrieve information about the offered data stream. This argument is
                             not required when running a MetaExtractionPlugin.
        :param tracelets: the tracelets of the trace.
        :param transformations: the data transformations of the trace.
        """
        self._grpc_handler = grpc_handler
        self._trace_id = trace_id
        self._properties = properties
        self._data_context = data_context
        self._tracelets: List[Tracelet] = []
        self._transformations = transformations
        self._next_child_id = 0
        self._new_types: Set[str] = set()
        self._new_properties: Dict[str, object] = {}

    def get(self, key: str, default=None):
        """Override :meth: `Trace.get`."""
        return self._properties[key] if key in self._properties else default

    def update(self, key_or_updates=None, value=None, data=None) -> None:
        """Override :meth: `ExtractionTrace.update`."""
        if key_or_updates is not None:
            types, properties = _extract_types_and_properties(self._properties, key_or_updates, value)
            self._new_types.update(types)
            self._new_properties.update(properties)
            self._properties.update(properties)
        if data is not None:
            self._grpc_handler.write_datas(self._trace_id, data)

    def add_tracelet(self, tracelet: Union[Tracelet, str],
                     value: Optional[Mapping[str, Any]] = None) -> None:
        """Override :meth: `ExtractionTrace.add_tracelet`."""
        if isinstance(tracelet, Tracelet) and not value:
            self._tracelets.append(tracelet)
        elif isinstance(tracelet, str) and value:
            self._tracelets.append(Tracelet(tracelet, value))
        else:
            raise TypeError('invalid arguments for adding tracelet, '
                            'need either tracelet type and value or Tracelet object')

    def add_transformation(self, data_type: str, transformation: Transformation) -> None:
        """Override :meth: `ExtractionTrace.add_transformation`."""
        if not data_type:
            raise ValueError('data_type is required')
        if transformation is None:
            raise ValueError('transformation is required')
        self._transformations.setdefault(data_type, []).append(transformation)

    def open(self, offset=0, size=None) -> BufferedReader:
        """Override :meth: `ExtractionTrace.open`."""
        data_size = self._data_context.data_size
        first_bytes = self._data_context.first_bytes
        if offset < 0 or offset > data_size:
            raise ValueError('Invalid value for offset')
        if size is None:
            size = data_size

        def read_from_known_trace(offset, size) -> GrpcAny:
            return self._grpc_handler.read(offset=offset, size=size, trace_uid=self._trace_id,
                                           data_type=self._data_context.data_type)

        return BufferedReader(_GrpcRawIO(read_from_known_trace, offset, size, first_bytes), buffer_size=1024 * 1024)

    def child_builder(self, name: str = None) -> ExtractionTraceBuilder:
        """Override :meth: `ExtractionTrace.child_builder`."""
        return GrpcExtractionTraceBuilder(self._grpc_handler, self._get_next_child_id(), name)

    def _get_next_child_id(self):
        next_id = self._trace_id + '-' + str(self._next_child_id)
        self._next_child_id = self._next_child_id + 1
        return next_id

    def _flush(self):
        """Send all new updates on this trace to the client side."""
        log.debug('Flushing trace builder {}', self._trace_id)

        if not self._has_changes():
            return

        self._grpc_handler.enrich_trace(self._trace_id,
                                        self._new_types,
                                        self._new_properties,
                                        self._tracelets,
                                        self._transformations)
        self._new_types = []
        self._new_properties = {}

    def _has_changes(self) -> bool:
        if self._new_types or self._new_properties or self._tracelets or self._transformations:
            return True
        return False

    def __eq__(self, other):
        if not isinstance(other, GrpcExtractionTrace):
            return False

        return self._properties == other._properties


class GrpcSearchResult(SearchResult):
    """Helper class that exposes a SearchResult that was exchanged with the gRPC protocol."""

    def __init__(self, total_results: int, traces_list: Sequence[SearchTrace]):
        """
        Initialize this SearchResult.

        :param total_results: Total results found matching a provided query.
        :param traces_list: List of traces that is returned when iterating over this SearchResult.
        """
        self._total_results = total_results
        self._traces_list = traces_list
        self._trace_index = 0

    def total_results(self) -> int:
        """Override :meth: `SearchResult.total_results`."""
        return self._total_results

    def __iter__(self) -> Iterator[SearchTrace]:
        """Iterate through the sequence of provided traces when this class with initialized."""
        # TODO: HANSKEN-15066 support search results of indefinite size
        while self._trace_index < len(self._traces_list):
            trace = self._traces_list[self._trace_index]
            self._trace_index += 1
            yield trace

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def _extract_types_and_properties(existing_properties: Union[Mapping, str], key_or_updates: Union[Mapping, str],
                                  value=None) -> Tuple[set, dict]:
    """
    Get the new types and properties defined by given 'key_or_updates' and 'value' properties.

    See `api.ExtractionTrace.update` for more information about their format.
    If a property was already set, an error is thrown (validated against 'existing_properties')

    :param existing_properties: the properties which were already set
    :param key_or_updates: the update key or mapping
    :param value: the update value in case 'key_or_updates' was a str
    :return: a tuple of a set of the types, and a mapping of the properties
    """
    validate_update_arguments(key_or_updates, value)

    types = set()
    properties = {}

    updates: Mapping[Any, Any]
    if isinstance(key_or_updates, str):
        updates = {key_or_updates: value}
    else:
        updates = key_or_updates

    for name, value in updates.items():
        if name in existing_properties:
            log.warning('property {} has already been set', name)

        if name == 'name':
            properties[name] = value
        elif '.' not in name:
            raise RuntimeError(f"property '{name}' format is invalid, "
                               f'a dot (.) between the type and the property is missing')
        else:
            # determine type from property name
            type = name[0:name.find('.')]

            # add type and property to list of new types
            types.add(type)
            properties[name] = value

    return types, properties


def _create_trace(grpc_handler: 'ProcessHandler', rpc_trace: RpcTrace, data_context: GrpcDataContext) -> \
        GrpcExtractionTrace:
    """Convert an RpcTrace into a GrpcExtractionTrace."""
    id, types, properties, tracelets, transformations = unpack.trace(rpc_trace)
    return GrpcExtractionTrace(grpc_handler=grpc_handler,
                               trace_id=id,
                               properties=properties,
                               data_context=data_context,
                               tracelets=tracelets,
                               transformations=transformations)


class GrpcSearchTrace(SearchTrace):
    """Helper class that exposes a SearchTrace that was exchanged with the gRPC protocol."""

    def __init__(self, grpc_handler: 'ProcessHandler', trace_id: str, properties: Dict[str, Any],
                 meta_datas: Mapping[str, RpcRandomAccessDataMeta]):
        """
        Initialize this SearchTrace.

        :param grpc_handler: ProcessHandler used to perform gRPC calls.
        :param trace_id: string representing the id of this trace.
        :param properties: key, value mapping of all known properties of this trace.
        :param meta_datas: Mapping of data_type to MetaData objects representing all data streams associated with this
                           trace.
        """
        self._properties = properties
        self._grpc_handler = grpc_handler
        self._trace_id = trace_id
        self._meta_datas = meta_datas

    def get(self, key: str, default=None):
        """Override :meth: `Trace.get`."""
        return self._properties[key] if key in self._properties else default

    def open(self, stream='raw', offset=0, size=None) -> BufferedReader:
        """Override :meth: `SearchTrace.open`."""
        if stream not in self._meta_datas:
            raise ValueError(f'Stream {stream} is not available on this trace. Available streams are '
                             f'{", ".join(self._meta_datas)}.')

        data_meta = self._meta_datas[stream]
        if offset < 0 or offset > data_meta.size:
            raise ValueError('Invalid value for offset')
        if size is None or offset + size > data_meta.size:
            size = data_meta.size - offset  # max available bytes

        def read_from_known_trace(offset: int, size: int) -> GrpcAny:
            return self._grpc_handler.read(offset=offset, size=size, trace_uid=self.get('uid'), data_type=stream)

        return BufferedReader(_GrpcRawIO(read_from_known_trace, offset, size, data_meta.firstBytes),
                              buffer_size=1024 * 1024)


class GrpcTraceSearcher(TraceSearcher):
    """Helper class that allows searching for traces using gRPC."""

    def __init__(self, handler: 'ProcessHandler'):
        """Initialize using a ProcessHandler, which forwards all request through gRPC."""
        self._handler = handler

    def search(self, query: str, count: int) -> SearchResult:
        """Override :meth: `TraceSearcher.search`."""
        return self._unpack_search_result(self._handler.search_traces(query, count))

    def _search_trace(self, rpc_trace: RpcSearchTrace) -> SearchTrace:
        """Create a SearchTrace from an RpcSearchTrace."""
        properties = unpack.trace_properties(rpc_trace.properties)
        datas = {data.type: data for data in rpc_trace.data}
        return GrpcSearchTrace(grpc_handler=self._handler, trace_id=rpc_trace.id, properties=properties,
                               meta_datas=datas)

    def _unpack_search_result(self, search_result: GrpcAny) -> SearchResult:
        """Create a SearchResult from an any message containing an RpcSearchResult."""
        result: RpcSearchResult = unpack.any(search_result, RpcSearchResult)
        search_traces = [self._search_trace(rpc_trace) for rpc_trace in result.traces]
        return GrpcSearchResult(result.totalResults, search_traces)


class GrpcWriter:
    """
    Class that writes data to a gRPC connection.

    Should be used with the ``with`` keyword:

    .. code-block:: python

        with GrpcWriter(trace_id, data_type, handler) as writer:
            write(bytes('test_string', 'UTF_8')
    """

    def __init__(self, trace_id: str, data_type: str, handler: 'ProcessHandler'):
        """
        Initialize this writer.

        :param trace_id: trace id of the trace the data will belong to
        :param data_type: data type to write.
        :param handler: ProcessHandler used to perform gRPC calls.
        """
        self.trace_id = trace_id
        self.data_type = data_type
        self.handler = handler

    def __enter__(self):
        """Send a start message to indicate we will start writing data to the client."""
        start_message = pack.begin_writing(self.trace_id, self.data_type)
        self.handler.handle_message(start_message)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Send a finish message indicating we are done writing data."""
        finish_message = pack.finish_writing(self.trace_id, self.data_type)
        self.handler.handle_message(finish_message)

    def write(self, data: bytes):
        """
        Write data to gRPC stream.

        This method sends data in separate chunks if it does not fit in one message.
        """
        size = len(data)
        offset = 0
        while offset < size:
            data_message = pack.write_data(self.trace_id, self.data_type, data[offset: offset + MAX_CHUNK_SIZE])
            self.handler.handle_message(data_message)
            offset += MAX_CHUNK_SIZE


class ProcessHandler:
    """
    Handles the bidirectional gRPC stream returned by the process method.

    The response iterator allows reading responses sent by the hansken client
    """

    SEARCH_REQUEST_COUNT_LIMIT = 50

    # if the request queue contains this sentinel, it indicates that no more items can be expected
    _sentinel = object()

    def __init__(self, response_iterator: Iterator[GrpcAny]):
        """
        Initialize this handler.

        :param response_iterator: Iterator returned by the gRPC framework containing client responses. If we wish to
                                  wait for a client message, call ``next(response_iterator)``.
        """
        log.debug('Creating a new GRPC process handler')
        # requests is a simple queue, all messages added to this queue are
        # sent to the client over gRPC. The zero indicates that this is an unbound queue
        self._requests: Queue[GrpcAny] = Queue(0)

        # gRPC responses are returned to this iterator
        self._response_iterator = response_iterator

        # stack trace ids, representing the current depth first pre-order scope, in order to translate it to in-order
        # the reason for this is that traces are not sent as soon as one is built (using TraceBuilder#build),
        # because the python API expects each parent trace to be built before their children
        # whereas the gRPC API expects a child to be finished before the parent
        self._trace_stack: List[str] = []

    def _handle_request(self, request) -> GrpcAny:
        """Block call, send a message to the client, and return it's reply."""
        self.handle_message(request)
        return next(self._response_iterator)

    def handle_message(self, message: Any):
        """
        Send a message to the client.

        :param message: gRPC any message
        """
        self._requests.put_nowait(pack.any(message))

    def write_datas(self, trace_id: str, data: Mapping[str, bytes]):
        """
        Write all given data streams to the remote for a given trace id.

        :param trace_id: id of the trace to attach data streams
        :param data: mapping from data type to bytes
        """
        for data_type in data:
            self.write_data(trace_id, data_type, data[data_type])

    def write_data(self, trace_id: str, data_type: str, data: bytes):
        """
        Write a single data stream to the client for a given trace id using a GrpcWriter.

        :param trace_id: id of the trace
        :param data_type: type of the data streams
        :param data: the actual data
        """
        with GrpcWriter(trace_id, data_type, self) as writer:
            writer.write(data)

    # TODO HANSKEN-15467 Trace Enrichment: pass a trace instead of 5 parameters
    def enrich_trace(self, trace_id: str, types: List[str], properties: Dict[str, Any],
                     tracelets: List[Tracelet], transformations: Dict[str, List[Transformation]]):
        """
        Send a gRPC message to enrich a trace with given properties, types and tracelets.

        :param trace_id: id of the trace
        :param types: types to enrich the trace with
        :param properties: properties to send
        :param tracelet_properties: tracelets to add
        """
        log.debug('Process handler enriches trace {} with properties {}', trace_id, properties)
        self._assert_correct_trace(trace_id)
        request = pack.trace_enrichment(trace_id, types, properties, tracelets, transformations)
        self.handle_message(request)

    def read(self, offset: int, size: int, trace_uid: str, data_type: str) -> GrpcAny:
        """
        Send a request to the client to read a single chunk of data from a specific data stream.

        :param offset: byte offset to start reading
        :param size: size of the data chunk
        :param trace_uid: uid of the trace the data stream is associated with
        :param data_type: type of the data
        :return: GrpcAny message containing the data
        """
        log.debug('Reading trace with offset {} and size {} and id {} and type {}', offset, size, trace_uid, data_type)
        rpc_read: RpcRead = pack.rpc_read(offset, size, trace_uid, data_type)
        return self._handle_request(rpc_read)

    def search_traces(self, query: str, count: int) -> GrpcAny:
        """
        Send a request to the client to search for traces.

        :param query: return traces matching this query
        :param count: maximum number of traces to return
        :return: GrpcAny message containing a `SearchResult`
        """
        # TODO: HANSKEN-15066 support search results of indefinite size
        if count > self.SEARCH_REQUEST_COUNT_LIMIT:  # safety check to fit answers into one gRPC message
            raise RuntimeError(f'search request count must not exceed the limit of '
                               f'{self.SEARCH_REQUEST_COUNT_LIMIT}')
        log.debug('Searching for {} additional traces with query {}', count, query)
        rpc_search_request = pack.rpc_search_request(query, count)
        return self._handle_request(rpc_search_request)

    def begin_child(self, trace_id: str, name: str) -> None:
        """
        Send a message to the client indicating that we are building a new child.

        Update the internal trace stack to stay aware on which child trace we are working.

        :param trace_id: id of the child trace
        :param name: name of the trace
        """
        log.debug('Process handler is beginning child trace {}', trace_id)
        while self._trace_stack and not self._is_direct_parent(self._trace_stack[-1], trace_id):
            # finish all out of scope traces
            self.handle_message(pack.finish_child(self._trace_stack.pop()))

        request = pack.begin_child(trace_id, name)
        self.handle_message(request)
        self._trace_stack.append(trace_id)

    def finish_child(self, trace_id: str) -> None:
        """
        Indicate that we finished building a child trace.

        :param trace_id: id of the child trace.
        """
        log.debug('Process handler is finishing child trace {}', trace_id)
        self._assert_correct_trace(trace_id)
        # not yet flushing here, because the python API stores parent before child (pre-order),
        # but the client expects the other way around (in-order)

    def finish(self):
        """Let the client know the server has finished processing this trace."""
        log.debug('Process handler is finishing processing.')
        request = RpcFinish()
        self.handle_message(request)
        self._finish()

    def finish_with_error(self, exception):
        """Let the client know an exception occurred while processing this trace."""
        log.warning('Finishing processing with an exception:', exc_info=True)
        try:
            rpc_partial_finish = pack.partial_finish_with_error(exception)
            self.handle_message(rpc_partial_finish)
        except Exception:
            # nothing more we can do now...  this is a last-resort catch to (hopefully) get the word out we're done
            log.warning('An exception occurred while reporting an error to the client')
            log.debug('with the following exception', exc_info=True)
        finally:
            # but do try to finish and let the client know it's over
            self._finish()

    def _finish(self):
        """Try to finish with the sentinel."""
        log.debug('Finish by putting the sentinel on the request queue')
        self._requests.put_nowait(self._sentinel)

    def iter(self) -> Iterator[GrpcAny]:
        """Return iterator object to which new messages are pushed, that can be returned to gRPC."""
        return iter(self._requests.get, self._sentinel)

    def _flush_traces(self) -> None:
        """Send all remaining finish messages for the trace ids on the id stack."""
        while self._trace_stack:
            self.handle_message(pack.finish_child(self._trace_stack.pop()))

    def _assert_correct_trace(self, trace_id: str) -> None:
        """Assert that the id passed is the one currently in scope based on the id stack."""
        if not self._trace_stack:
            # if no trace on the stack, assert that we are working on the root
            if '-' not in trace_id:
                return
            raise RuntimeError('trying to update trace {} before initializing it'.format(trace_id))
        # assert that the current trace on the top of the stack is the one we are working on
        if self._trace_stack[-1] != trace_id:
            raise RuntimeError(
                'trying to update trace {} before building trace {}'.format(trace_id, self._trace_stack[-1])
            )

    @staticmethod
    def _is_direct_parent(parent_id: str, child_id: str) -> bool:
        return child_id.startswith(parent_id) and len(parent_id) == child_id.rfind('-')


class ExtractionPluginServicer(ExtractionPluginServiceServicer):
    """This is our implementation of the gRPC generated ExtractionPluginServiceServicer."""

    def __init__(self, extraction_plugin_class: Callable[[], BaseExtractionPlugin]):
        """
        Initialize this servicer.

        :param extraction_plugin_class: Method returning an instance of a BaseExtractionPlugin.
        """
        self._plugin = extraction_plugin_class()

    def pluginInfo(self, request, context: grpc.RpcContext) -> RpcPluginInfo:  # noqa: N802
        """Convert Extraction Plugin plugin info to gRPC plugininfo and returns it to the requester."""
        return pack.plugin_info(self._plugin.plugin_info(), self._plugin)

    def process(self, response_iterator: Iterator[GrpcAny], context: grpc.RpcContext) -> Iterator[GrpcAny]:
        """
        Call the plugin process method.

        Asynchronous process method. This is where the plugin process method gets called
        in a new thread. This call will return immediately. The process thread will do the processing of the trace.
        After the thread completes, a finish message is sent to the client.

        :param response_iterator: The GRPC handler's queue iterator
        :param context: The trace data_context
        """
        grpc_handler = ProcessHandler(response_iterator)
        try:
            log.debug('Plugin servicer process started.')
            self._process(response_iterator, context, grpc_handler)
        except Exception as exception:
            log.error('An exception occurred during processing')
            grpc_handler.finish_with_error(exception)
        finally:
            # Return the iterator to get the next message or the sentinel, which marks the last entry.
            log.debug('Plugin servicer process finished.')
            return grpc_handler.iter()

    @staticmethod
    def _start_message_to_context(start_message: RpcStart) -> GrpcDataContext:
        return GrpcDataContext(data_type=start_message.dataContext.dataType,
                               data_size=start_message.dataContext.data.size,
                               first_bytes=start_message.dataContext.data.firstBytes)

    def _process(self, response_iterator, grpc_context, grpc_handler):
        first_message = next(response_iterator)
        if not first_message.Is(RpcStart.DESCRIPTOR):
            log.warning('Expecting RpcStart, but received unexpected message: {}', first_message)
            raise RuntimeError('Expecting RpcStart message')

        start_message = unpack.any(first_message, RpcStart)

        # process in a different thread, so that we can keep this thread to send messages to the client (Hansken)
        if isinstance(self._plugin, ExtractionPlugin):
            data_context = self._start_message_to_context(start_message)
            trace = _create_trace(grpc_handler=grpc_handler, rpc_trace=start_message.trace, data_context=data_context)

            def run_process():
                cast(ExtractionPlugin, self._plugin).process(trace, data_context)

            threading.Thread(target=self._process_trace,
                             args=(run_process, trace, grpc_handler, data_context),
                             daemon=True).start()

        elif isinstance(self._plugin, MetaExtractionPlugin):
            trace = _create_trace(grpc_handler=grpc_handler, rpc_trace=start_message.trace, data_context=None)

            def run_process():
                cast(MetaExtractionPlugin, self._plugin).process(trace)

            threading.Thread(target=self._process_trace,
                             args=(run_process, trace, grpc_handler, None),
                             daemon=True).start()

        elif isinstance(self._plugin, DeferredExtractionPlugin):
            data_context = self._start_message_to_context(start_message)
            trace = _create_trace(grpc_handler=grpc_handler, rpc_trace=start_message.trace, data_context=data_context)
            searcher = GrpcTraceSearcher(grpc_handler)

            def run_process():
                cast(DeferredExtractionPlugin, self._plugin).process(trace, data_context, searcher)

            threading.Thread(target=self._process_trace,
                             args=(run_process, trace, grpc_handler, data_context),
                             daemon=True).start()

        else:
            raise RuntimeError('Unsupported type of plugin: {}', str(type(self._plugin)))

    def _process_trace(self, run_process: Callable[[], None],
                       trace: GrpcExtractionTrace,
                       grpc_handler: ProcessHandler,
                       context: DataContext):
        try:
            self._log_start_processing(trace, context)
            run_process()
            self._flush_trace_tree(grpc_handler, trace)
            grpc_handler.finish()
            log.info('Finished processing trace with id: {}', trace._trace_id)
        except Exception as exception:
            log.exception('Error during processing trace with id: {}', trace._trace_id)
            try:
                self._flush_trace_tree(grpc_handler, trace)
            finally:
                grpc_handler.finish_with_error(exception)

    def _log_start_processing(self, trace: GrpcExtractionTrace, context: DataContext):
        # meta data_context has no associated data stream
        if context is None:
            log.info('Started processing trace with id: {}, data type: meta', trace._trace_id)
        else:
            log.info('Started processing trace with id: {}, data type: {}, size: {}',
                     trace._trace_id,
                     context.data_type,
                     context.data_size)

    def _flush_trace_tree(self, grpc_handler: ProcessHandler, trace: GrpcExtractionTrace):
        # flush cached child traces
        grpc_handler._flush_traces()
        # flush updated information on root trace
        trace._flush()


class HealthServiceServicer(HealthServicer):
    """HealthServicer implementation to expose the plugin status."""

    def Check(self, request, context):  # noqa: N802
        """Return SERVING status."""
        return HealthCheckResponse(status=HealthCheckResponse.SERVING)

    def Watch(self, request, context):  # noqa: N802
        """Yield SERVING status."""
        yield HealthCheckResponse(status=HealthCheckResponse.SERVING)


def _start_server(extraction_plugin_class: Type[BaseExtractionPlugin], address: str) -> grpc.Server:
    """
    Start extraction plugin server.

    :extraction_plugin_class: Class of the extraction plugin implementation
    :address: Address serving this server
    :return: gRPC server object
    """
    options = (('grpc.max_send_message_length', MAX_MESSAGE_SIZE),
               ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE),
               ('grpc.so_reuseport', 0))
    # TODO Is 16 the correct number? Make configurable or investigate
    num_workers = 16
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=num_workers), options=options)
    add_ExtractionPluginServiceServicer_to_server(ExtractionPluginServicer(extraction_plugin_class), server)
    add_HealthServicer_to_server(HealthServiceServicer(), server)
    server.add_insecure_port(address)
    log.info('Starting GRPC Extraction Plugin server with {} workers. Listening on {}.', num_workers, address)
    log.info('Plugin running with API version {}', api_version)
    server.start()
    return server


@contextmanager
def serve(extraction_plugin_class: Type[BaseExtractionPlugin], address: str) -> Generator[grpc.Server, None, None]:
    """
    Return data_context manager to start a server, so a server can be started using the ``with`` keyword.

    :extraction_plugin_class: Class of the extraction plugin implementation
    :address: Address serving this server
    :return: contextmanager of extraction plugin server
    """
    server = _start_server(extraction_plugin_class, address)
    yield server
    server.stop(None)


def serve_indefinitely(extraction_plugin_class: Type[BaseExtractionPlugin], address: str):
    """
    Start extraction plugin server that runs until it is explicitly killed.

    This method installs a SIGTERM handler, so the extraction plugin server
    will be stopped gracefully when the server(container) is requested to stop.
    Therefore, this method can only be called from the main-thread.

    :extraction_plugin_class: Class of the extraction plugin implementation
    :address: Address serving this server
    """
    server = _start_server(extraction_plugin_class, address)

    def handle_signal(*_):
        log.info('Received SIGTERM, stopping the plugin server now')
        log.info('Waiting max 5 seconds for requests to complete')
        server.stop(5).wait(5)
        log.info('Shut down gracefully')

    signal(SIGTERM, handle_signal)
    signal(SIGINT, handle_signal)

    server.wait_for_termination()
    log.info('Server terminated')

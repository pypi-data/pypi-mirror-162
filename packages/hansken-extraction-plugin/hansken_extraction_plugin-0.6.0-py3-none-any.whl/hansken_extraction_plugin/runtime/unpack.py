"""Methods to unpack gRPC messages to sdk classes."""
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Tuple, Type, Union

from google.protobuf.any_pb2 import Any as GrpcAny
from google.protobuf.message import Message
from hansken.util import GeographicLocation, Vector
import pytz

from hansken_extraction_plugin.api.tracelet import Tracelet
from hansken_extraction_plugin.api.transformation import Range, RangedTransformation, Transformation
from hansken_extraction_plugin.framework.DataMessages_pb2 import RpcDataStreamTransformation, RpcRange, \
    RpcRangedTransformation, RpcTrace, RpcTracelet, RpcTraceProperty
from hansken_extraction_plugin.framework.PrimitiveMessages_pb2 import RpcBoolean, RpcBytes, RpcDouble, RpcEmptyList, \
    RpcEmptyMap, RpcInteger, RpcIsoDateString, RpcLatLong, RpcLong, RpcLongList, RpcMap, RpcNull, RpcString, \
    RpcStringList, RpcStringMap, RpcUnixTime, RpcVector, RpcZonedDateTime


def any(message: GrpcAny, unpacker: Callable[[], Message]):
    """
    Unwrap a GrpcAny message and return the containing message.

    :param message: message to unwrap
    :param unpacker: method to convert GrpcAny message to the specific message
    :return: unwrapped message
    """
    unpacked = unpacker()
    message.Unpack(unpacked)
    return unpacked


def _rpc_zoned_date_time(zdt: RpcZonedDateTime) -> datetime:
    epoch_nanos_in_seconds: float = zdt.nanoOfSecond / 1000_000_000.0
    timezone = pytz.timezone(zdt.zoneId)

    return datetime.fromtimestamp(zdt.epochSecond + epoch_nanos_in_seconds, timezone)


def _rpc_unix_time(ut: RpcUnixTime) -> datetime:
    epoch_seconds: float = ut.value / 1000.0

    return datetime.fromtimestamp(epoch_seconds, pytz.utc)


def _map(rpc_map: RpcMap) -> Dict[str, Any]:
    converted_map: Dict[str, Any] = {}
    for key, value in rpc_map.entries.items():
        converted_map[key] = _primitive(value)
    return converted_map


_primitive_matchers: Dict[
    Type[Union[
        RpcNull,
        RpcBytes,
        RpcBoolean,
        RpcInteger,
        RpcLong,
        RpcDouble,
        RpcString,
        RpcEmptyList,
        RpcStringList,
        RpcLongList,
        RpcEmptyMap,
        RpcMap,
        RpcStringMap,
        RpcUnixTime,
        RpcZonedDateTime,
        RpcIsoDateString,
        RpcLatLong,
        RpcVector,
    ]],
    Callable[[Any], Any]
] = {
    RpcNull: lambda value: None,
    RpcBytes: lambda value: value.value,
    RpcBoolean: lambda value: value.value,
    RpcInteger: lambda value: value.value,
    RpcLong: lambda value: value.value,
    RpcDouble: lambda value: value.value,
    RpcString: lambda value: value.value,
    RpcEmptyList: lambda value: [],
    RpcStringList: lambda value: value.values,
    RpcLongList: lambda value: value.values,
    RpcEmptyMap: lambda value: {},
    RpcMap: lambda value: _map(value),
    RpcStringMap: lambda value: value.entries,
    RpcUnixTime: lambda value: _rpc_unix_time(value),
    RpcZonedDateTime: lambda value: _rpc_zoned_date_time(value),
    RpcIsoDateString: lambda value: datetime.strptime(value.value, '%Y-%m-%dT%H:%M:%S%z'),
    RpcLatLong: lambda value: GeographicLocation(value.latitude, value.longitude),
    RpcVector: lambda value: Vector(value.value),
}


def _primitive(value: GrpcAny):
    # unpacks a primitive value that is wrapped inside an (Grpc)Any
    for matchertype, unpacker in _primitive_matchers.items():
        if value.Is(matchertype.DESCRIPTOR):
            return unpacker(any(value, matchertype))

    raise RuntimeError('unable to unpack primitive value of type {} '.format(value))


def _tracelet(rpc_tracelet: RpcTracelet) -> Tracelet:
    value = {property.name: _primitive(property.value) for property in rpc_tracelet.properties}
    return Tracelet(rpc_tracelet.name, value)


def _transformation(rpc_data_stream_transformation: RpcDataStreamTransformation) -> Tuple[str, List[Transformation]]:
    transformations: List[Transformation] = []
    for rpc_transformation in rpc_data_stream_transformation.transformations:
        type = rpc_transformation.WhichOneof('value')
        if rpc_transformation.rangedTransformation:
            transformations.append(_ranged_transformation(rpc_transformation.rangedTransformation))
        else:
            raise ValueError(f'Unsupported transformation type: {type}')

    return rpc_data_stream_transformation.dataType, transformations


def _ranged_transformation(rpc_ranged_transformation: RpcRangedTransformation) -> RangedTransformation:
    return RangedTransformation([_range(range) for range in rpc_ranged_transformation.ranges])


def _range(rpc_range: RpcRange) -> Range:
    return Range(offset=rpc_range.offset, length=rpc_range.length)


def trace(trace: RpcTrace) -> Tuple[str, List[str], Dict[str, Any], List[Tracelet], Dict[str, List[Transformation]]]:
    """
    Convert a RpcTrace to a quintuplet (id, types, properties, tracelets, transformations) of the trace.

    :param trace: the trace to convert.
    :return: quintuplet with id, types, properties, tracelets and transformations.
    """
    id: str = trace.id
    types: List[str] = list(trace.types)
    properties: Dict[str, Any] = {prop.name: _primitive(prop.value) for prop in trace.properties}
    tracelets = [_tracelet(tracelet) for tracelet in trace.tracelets]
    transformation_tuples = [_transformation(transformation) for transformation in trace.transformations]
    transformations: Dict[str, List[Transformation]] = dict(transformation_tuples)
    return id, types, properties, tracelets, transformations


def trace_properties(properties: Iterable[RpcTraceProperty]) -> Dict[str, Any]:
    """
    Unpack a list of RpcTraceProperties to a dictionary of property name to their values.

    :param properties: iterable of gRPC trace properties to unpack
    :return: dictionary of property names to unpacked values
    """
    return {prop.name: _primitive(prop.value) for prop in properties}


def bytez(bites: GrpcAny) -> bytes:
    """
    Convert GrpcAny to a primitive bytes() stream.

    @param bites: gRPC message containing bytes
    @return: primitive bytes()
    """
    return _primitive(bites)

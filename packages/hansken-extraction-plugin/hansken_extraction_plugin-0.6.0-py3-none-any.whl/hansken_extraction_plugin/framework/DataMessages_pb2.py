# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: hansken_extraction_plugin/framework/DataMessages.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n6hansken_extraction_plugin/framework/DataMessages.proto\x12\"org.hansken.extraction.plugin.grpc\x1a\x19google/protobuf/any.proto\"\x80\x04\n\rRpcPluginInfo\x12?\n\x04type\x18\x01 \x01(\x0e\x32\x31.org.hansken.extraction.plugin.grpc.RpcPluginType\x12\x12\n\napiVersion\x18\x02 \x01(\t\x12\x10\n\x04name\x18\x03 \x01(\tB\x02\x18\x01\x12\x0f\n\x07version\x18\x04 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x05 \x01(\t\x12=\n\x06\x61uthor\x18\x06 \x01(\x0b\x32-.org.hansken.extraction.plugin.grpc.RpcAuthor\x12\x41\n\x08maturity\x18\x07 \x01(\x0e\x32/.org.hansken.extraction.plugin.grpc.RpcMaturity\x12\x0f\n\x07matcher\x18\x08 \x01(\t\x12\x12\n\nwebpageUrl\x18\t \x01(\t\x12\x1a\n\x12\x64\x65\x66\x65rredIterations\x18\n \x01(\x05\x12\x43\n\x02id\x18\x0b \x01(\x0b\x32\x37.org.hansken.extraction.plugin.grpc.RpcPluginIdentifier\x12\x0f\n\x07license\x18\r \x01(\t\x12I\n\tresources\x18\x0e \x01(\x0b\x32\x36.org.hansken.extraction.plugin.grpc.RpcPluginResources\"E\n\x13RpcPluginIdentifier\x12\x0e\n\x06\x64omain\x18\x01 \x01(\t\x12\x10\n\x08\x63\x61tegory\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\">\n\tRpcAuthor\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05\x65mail\x18\x02 \x01(\t\x12\x14\n\x0corganisation\x18\x03 \x01(\t\"7\n\x12RpcPluginResources\x12\x0e\n\x06maxCpu\x18\x01 \x01(\x02\x12\x11\n\tmaxMemory\x18\x02 \x01(\r\"E\n\x10RpcTraceProperty\x12\x0c\n\x04name\x18\x01 \x01(\t\x12#\n\x05value\x18\x02 \x01(\x0b\x32\x14.google.protobuf.Any\"e\n\x0bRpcTracelet\x12\x0c\n\x04name\x18\x01 \x01(\t\x12H\n\nproperties\x18\x02 \x03(\x0b\x32\x34.org.hansken.extraction.plugin.grpc.RpcTraceProperty\"\x8d\x02\n\x08RpcTrace\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05types\x18\x02 \x03(\t\x12H\n\nproperties\x18\x03 \x03(\x0b\x32\x34.org.hansken.extraction.plugin.grpc.RpcTraceProperty\x12\x42\n\ttracelets\x18\x04 \x03(\x0b\x32/.org.hansken.extraction.plugin.grpc.RpcTracelet\x12X\n\x0ftransformations\x18\x05 \x03(\x0b\x32?.org.hansken.extraction.plugin.grpc.RpcDataStreamTransformation\"\x7f\n\x1bRpcDataStreamTransformation\x12\x10\n\x08\x64\x61taType\x18\x01 \x01(\t\x12N\n\x0ftransformations\x18\x02 \x03(\x0b\x32\x35.org.hansken.extraction.plugin.grpc.RpcTransformation\"\xc0\x01\n\x0eRpcSearchTrace\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05types\x18\x02 \x03(\t\x12H\n\nproperties\x18\x03 \x03(\x0b\x32\x34.org.hansken.extraction.plugin.grpc.RpcTraceProperty\x12I\n\x04\x64\x61ta\x18\x04 \x03(\x0b\x32;.org.hansken.extraction.plugin.grpc.RpcRandomAccessDataMeta\"m\n\x0eRpcDataContext\x12\x10\n\x08\x64\x61taType\x18\x01 \x01(\t\x12I\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32;.org.hansken.extraction.plugin.grpc.RpcRandomAccessDataMeta\"I\n\x17RpcRandomAccessDataMeta\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0c\n\x04size\x18\x02 \x01(\x03\x12\x12\n\nfirstBytes\x18\x03 \x01(\x0c\"y\n\x11RpcTransformation\x12[\n\x14rangedTransformation\x18\x01 \x01(\x0b\x32;.org.hansken.extraction.plugin.grpc.RpcRangedTransformationH\x00\x42\x07\n\x05value\"W\n\x17RpcRangedTransformation\x12<\n\x06ranges\x18\x01 \x03(\x0b\x32,.org.hansken.extraction.plugin.grpc.RpcRange\"*\n\x08RpcRange\x12\x0e\n\x06offset\x18\x01 \x01(\x03\x12\x0e\n\x06length\x18\x02 \x01(\x03*]\n\rRpcPluginType\x12\x14\n\x10\x45xtractionPlugin\x10\x00\x12\x18\n\x14MetaExtractionPlugin\x10\x01\x12\x1c\n\x18\x44\x65\x66\x65rredExtractionPlugin\x10\x02*H\n\x0bRpcMaturity\x12\x12\n\x0eProofOfConcept\x10\x00\x12\x10\n\x0cReadyForTest\x10\x01\x12\x13\n\x0fProductionReady\x10\x02\x42&\n\"org.hansken.extraction.plugin.grpcP\x01\x62\x06proto3')

_RPCPLUGINTYPE = DESCRIPTOR.enum_types_by_name['RpcPluginType']
RpcPluginType = enum_type_wrapper.EnumTypeWrapper(_RPCPLUGINTYPE)
_RPCMATURITY = DESCRIPTOR.enum_types_by_name['RpcMaturity']
RpcMaturity = enum_type_wrapper.EnumTypeWrapper(_RPCMATURITY)
ExtractionPlugin = 0
MetaExtractionPlugin = 1
DeferredExtractionPlugin = 2
ProofOfConcept = 0
ReadyForTest = 1
ProductionReady = 2


_RPCPLUGININFO = DESCRIPTOR.message_types_by_name['RpcPluginInfo']
_RPCPLUGINIDENTIFIER = DESCRIPTOR.message_types_by_name['RpcPluginIdentifier']
_RPCAUTHOR = DESCRIPTOR.message_types_by_name['RpcAuthor']
_RPCPLUGINRESOURCES = DESCRIPTOR.message_types_by_name['RpcPluginResources']
_RPCTRACEPROPERTY = DESCRIPTOR.message_types_by_name['RpcTraceProperty']
_RPCTRACELET = DESCRIPTOR.message_types_by_name['RpcTracelet']
_RPCTRACE = DESCRIPTOR.message_types_by_name['RpcTrace']
_RPCDATASTREAMTRANSFORMATION = DESCRIPTOR.message_types_by_name['RpcDataStreamTransformation']
_RPCSEARCHTRACE = DESCRIPTOR.message_types_by_name['RpcSearchTrace']
_RPCDATACONTEXT = DESCRIPTOR.message_types_by_name['RpcDataContext']
_RPCRANDOMACCESSDATAMETA = DESCRIPTOR.message_types_by_name['RpcRandomAccessDataMeta']
_RPCTRANSFORMATION = DESCRIPTOR.message_types_by_name['RpcTransformation']
_RPCRANGEDTRANSFORMATION = DESCRIPTOR.message_types_by_name['RpcRangedTransformation']
_RPCRANGE = DESCRIPTOR.message_types_by_name['RpcRange']
RpcPluginInfo = _reflection.GeneratedProtocolMessageType('RpcPluginInfo', (_message.Message,), {
  'DESCRIPTOR' : _RPCPLUGININFO,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcPluginInfo)
  })
_sym_db.RegisterMessage(RpcPluginInfo)

RpcPluginIdentifier = _reflection.GeneratedProtocolMessageType('RpcPluginIdentifier', (_message.Message,), {
  'DESCRIPTOR' : _RPCPLUGINIDENTIFIER,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcPluginIdentifier)
  })
_sym_db.RegisterMessage(RpcPluginIdentifier)

RpcAuthor = _reflection.GeneratedProtocolMessageType('RpcAuthor', (_message.Message,), {
  'DESCRIPTOR' : _RPCAUTHOR,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcAuthor)
  })
_sym_db.RegisterMessage(RpcAuthor)

RpcPluginResources = _reflection.GeneratedProtocolMessageType('RpcPluginResources', (_message.Message,), {
  'DESCRIPTOR' : _RPCPLUGINRESOURCES,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcPluginResources)
  })
_sym_db.RegisterMessage(RpcPluginResources)

RpcTraceProperty = _reflection.GeneratedProtocolMessageType('RpcTraceProperty', (_message.Message,), {
  'DESCRIPTOR' : _RPCTRACEPROPERTY,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcTraceProperty)
  })
_sym_db.RegisterMessage(RpcTraceProperty)

RpcTracelet = _reflection.GeneratedProtocolMessageType('RpcTracelet', (_message.Message,), {
  'DESCRIPTOR' : _RPCTRACELET,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcTracelet)
  })
_sym_db.RegisterMessage(RpcTracelet)

RpcTrace = _reflection.GeneratedProtocolMessageType('RpcTrace', (_message.Message,), {
  'DESCRIPTOR' : _RPCTRACE,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcTrace)
  })
_sym_db.RegisterMessage(RpcTrace)

RpcDataStreamTransformation = _reflection.GeneratedProtocolMessageType('RpcDataStreamTransformation', (_message.Message,), {
  'DESCRIPTOR' : _RPCDATASTREAMTRANSFORMATION,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcDataStreamTransformation)
  })
_sym_db.RegisterMessage(RpcDataStreamTransformation)

RpcSearchTrace = _reflection.GeneratedProtocolMessageType('RpcSearchTrace', (_message.Message,), {
  'DESCRIPTOR' : _RPCSEARCHTRACE,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcSearchTrace)
  })
_sym_db.RegisterMessage(RpcSearchTrace)

RpcDataContext = _reflection.GeneratedProtocolMessageType('RpcDataContext', (_message.Message,), {
  'DESCRIPTOR' : _RPCDATACONTEXT,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcDataContext)
  })
_sym_db.RegisterMessage(RpcDataContext)

RpcRandomAccessDataMeta = _reflection.GeneratedProtocolMessageType('RpcRandomAccessDataMeta', (_message.Message,), {
  'DESCRIPTOR' : _RPCRANDOMACCESSDATAMETA,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcRandomAccessDataMeta)
  })
_sym_db.RegisterMessage(RpcRandomAccessDataMeta)

RpcTransformation = _reflection.GeneratedProtocolMessageType('RpcTransformation', (_message.Message,), {
  'DESCRIPTOR' : _RPCTRANSFORMATION,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcTransformation)
  })
_sym_db.RegisterMessage(RpcTransformation)

RpcRangedTransformation = _reflection.GeneratedProtocolMessageType('RpcRangedTransformation', (_message.Message,), {
  'DESCRIPTOR' : _RPCRANGEDTRANSFORMATION,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcRangedTransformation)
  })
_sym_db.RegisterMessage(RpcRangedTransformation)

RpcRange = _reflection.GeneratedProtocolMessageType('RpcRange', (_message.Message,), {
  'DESCRIPTOR' : _RPCRANGE,
  '__module__' : 'hansken_extraction_plugin.framework.DataMessages_pb2'
  # @@protoc_insertion_point(class_scope:org.hansken.extraction.plugin.grpc.RpcRange)
  })
_sym_db.RegisterMessage(RpcRange)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\"org.hansken.extraction.plugin.grpcP\001'
  _RPCPLUGININFO.fields_by_name['name']._options = None
  _RPCPLUGININFO.fields_by_name['name']._serialized_options = b'\030\001'
  _RPCPLUGINTYPE._serialized_start=2040
  _RPCPLUGINTYPE._serialized_end=2133
  _RPCMATURITY._serialized_start=2135
  _RPCMATURITY._serialized_end=2207
  _RPCPLUGININFO._serialized_start=122
  _RPCPLUGININFO._serialized_end=634
  _RPCPLUGINIDENTIFIER._serialized_start=636
  _RPCPLUGINIDENTIFIER._serialized_end=705
  _RPCAUTHOR._serialized_start=707
  _RPCAUTHOR._serialized_end=769
  _RPCPLUGINRESOURCES._serialized_start=771
  _RPCPLUGINRESOURCES._serialized_end=826
  _RPCTRACEPROPERTY._serialized_start=828
  _RPCTRACEPROPERTY._serialized_end=897
  _RPCTRACELET._serialized_start=899
  _RPCTRACELET._serialized_end=1000
  _RPCTRACE._serialized_start=1003
  _RPCTRACE._serialized_end=1272
  _RPCDATASTREAMTRANSFORMATION._serialized_start=1274
  _RPCDATASTREAMTRANSFORMATION._serialized_end=1401
  _RPCSEARCHTRACE._serialized_start=1404
  _RPCSEARCHTRACE._serialized_end=1596
  _RPCDATACONTEXT._serialized_start=1598
  _RPCDATACONTEXT._serialized_end=1707
  _RPCRANDOMACCESSDATAMETA._serialized_start=1709
  _RPCRANDOMACCESSDATAMETA._serialized_end=1782
  _RPCTRANSFORMATION._serialized_start=1784
  _RPCTRANSFORMATION._serialized_end=1905
  _RPCRANGEDTRANSFORMATION._serialized_start=1907
  _RPCRANGEDTRANSFORMATION._serialized_end=1994
  _RPCRANGE._serialized_start=1996
  _RPCRANGE._serialized_end=2038
# @@protoc_insertion_point(module_scope)

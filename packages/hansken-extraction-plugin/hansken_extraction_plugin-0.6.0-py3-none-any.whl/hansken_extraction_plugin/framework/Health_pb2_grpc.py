# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from hansken_extraction_plugin.framework import Health_pb2 as hansken__extraction__plugin_dot_framework_dot_Health__pb2


class HealthStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Check = channel.unary_unary(
                '/grpc.health.v1.Health/Check',
                request_serializer=hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckRequest.SerializeToString,
                response_deserializer=hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckResponse.FromString,
                )
        self.Watch = channel.unary_stream(
                '/grpc.health.v1.Health/Watch',
                request_serializer=hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckRequest.SerializeToString,
                response_deserializer=hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckResponse.FromString,
                )


class HealthServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Check(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Watch(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_HealthServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Check': grpc.unary_unary_rpc_method_handler(
                    servicer.Check,
                    request_deserializer=hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckRequest.FromString,
                    response_serializer=hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckResponse.SerializeToString,
            ),
            'Watch': grpc.unary_stream_rpc_method_handler(
                    servicer.Watch,
                    request_deserializer=hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckRequest.FromString,
                    response_serializer=hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grpc.health.v1.Health', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Health(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Check(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.health.v1.Health/Check',
            hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckRequest.SerializeToString,
            hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Watch(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/grpc.health.v1.Health/Watch',
            hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckRequest.SerializeToString,
            hansken__extraction__plugin_dot_framework_dot_Health__pb2.HealthCheckResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

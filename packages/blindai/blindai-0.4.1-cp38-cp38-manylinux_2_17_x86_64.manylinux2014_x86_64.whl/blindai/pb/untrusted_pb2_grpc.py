# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import untrusted_pb2 as untrusted__pb2


class AttestationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetCertificate = channel.unary_unary(
                '/untrusted.Attestation/GetCertificate',
                request_serializer=untrusted__pb2.GetCertificateRequest.SerializeToString,
                response_deserializer=untrusted__pb2.GetCertificateReply.FromString,
                )
        self.GetToken = channel.unary_unary(
                '/untrusted.Attestation/GetToken',
                request_serializer=untrusted__pb2.GetTokenRequest.SerializeToString,
                response_deserializer=untrusted__pb2.GetTokenReply.FromString,
                )
        self.GetSgxQuoteWithCollateral = channel.unary_unary(
                '/untrusted.Attestation/GetSgxQuoteWithCollateral',
                request_serializer=untrusted__pb2.GetSgxQuoteWithCollateralRequest.SerializeToString,
                response_deserializer=untrusted__pb2.GetSgxQuoteWithCollateralReply.FromString,
                )
        self.GetServerInfo = channel.unary_unary(
                '/untrusted.Attestation/GetServerInfo',
                request_serializer=untrusted__pb2.GetServerInfoRequest.SerializeToString,
                response_deserializer=untrusted__pb2.GetServerInfoReply.FromString,
                )


class AttestationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetCertificate(self, request, context):
        """Get JWT Token from Azure Attestation
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetToken(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetSgxQuoteWithCollateral(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetServerInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AttestationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetCertificate': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCertificate,
                    request_deserializer=untrusted__pb2.GetCertificateRequest.FromString,
                    response_serializer=untrusted__pb2.GetCertificateReply.SerializeToString,
            ),
            'GetToken': grpc.unary_unary_rpc_method_handler(
                    servicer.GetToken,
                    request_deserializer=untrusted__pb2.GetTokenRequest.FromString,
                    response_serializer=untrusted__pb2.GetTokenReply.SerializeToString,
            ),
            'GetSgxQuoteWithCollateral': grpc.unary_unary_rpc_method_handler(
                    servicer.GetSgxQuoteWithCollateral,
                    request_deserializer=untrusted__pb2.GetSgxQuoteWithCollateralRequest.FromString,
                    response_serializer=untrusted__pb2.GetSgxQuoteWithCollateralReply.SerializeToString,
            ),
            'GetServerInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetServerInfo,
                    request_deserializer=untrusted__pb2.GetServerInfoRequest.FromString,
                    response_serializer=untrusted__pb2.GetServerInfoReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'untrusted.Attestation', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Attestation(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetCertificate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/untrusted.Attestation/GetCertificate',
            untrusted__pb2.GetCertificateRequest.SerializeToString,
            untrusted__pb2.GetCertificateReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetToken(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/untrusted.Attestation/GetToken',
            untrusted__pb2.GetTokenRequest.SerializeToString,
            untrusted__pb2.GetTokenReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetSgxQuoteWithCollateral(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/untrusted.Attestation/GetSgxQuoteWithCollateral',
            untrusted__pb2.GetSgxQuoteWithCollateralRequest.SerializeToString,
            untrusted__pb2.GetSgxQuoteWithCollateralReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetServerInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/untrusted.Attestation/GetServerInfo',
            untrusted__pb2.GetServerInfoRequest.SerializeToString,
            untrusted__pb2.GetServerInfoReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

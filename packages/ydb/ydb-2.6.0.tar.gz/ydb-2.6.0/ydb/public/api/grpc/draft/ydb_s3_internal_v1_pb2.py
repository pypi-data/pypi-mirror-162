# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ydb/public/api/grpc/draft/ydb_s3_internal_v1.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ydb.public.api.protos import ydb_s3_internal_pb2 as ydb_dot_public_dot_api_dot_protos_dot_ydb__s3__internal__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='ydb/public/api/grpc/draft/ydb_s3_internal_v1.proto',
  package='Ydb.S3Internal.V1',
  syntax='proto3',
  serialized_options=b'\n\035com.yandex.ydb.s3_internal.v1',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n2ydb/public/api/grpc/draft/ydb_s3_internal_v1.proto\x12\x11Ydb.S3Internal.V1\x1a+ydb/public/api/protos/ydb_s3_internal.proto2e\n\x11S3InternalService\x12P\n\tS3Listing\x12 .Ydb.S3Internal.S3ListingRequest\x1a!.Ydb.S3Internal.S3ListingResponseB\x1f\n\x1d\x63om.yandex.ydb.s3_internal.v1b\x06proto3'
  ,
  dependencies=[ydb_dot_public_dot_api_dot_protos_dot_ydb__s3__internal__pb2.DESCRIPTOR,])



_sym_db.RegisterFileDescriptor(DESCRIPTOR)


DESCRIPTOR._options = None

_S3INTERNALSERVICE = _descriptor.ServiceDescriptor(
  name='S3InternalService',
  full_name='Ydb.S3Internal.V1.S3InternalService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=118,
  serialized_end=219,
  methods=[
  _descriptor.MethodDescriptor(
    name='S3Listing',
    full_name='Ydb.S3Internal.V1.S3InternalService.S3Listing',
    index=0,
    containing_service=None,
    input_type=ydb_dot_public_dot_api_dot_protos_dot_ydb__s3__internal__pb2._S3LISTINGREQUEST,
    output_type=ydb_dot_public_dot_api_dot_protos_dot_ydb__s3__internal__pb2._S3LISTINGRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_S3INTERNALSERVICE)

DESCRIPTOR.services_by_name['S3InternalService'] = _S3INTERNALSERVICE

# @@protoc_insertion_point(module_scope)

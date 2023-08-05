# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ydb/public/api/grpc/ydb_auth_v1.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ydb.public.api.protos import ydb_auth_pb2 as ydb_dot_public_dot_api_dot_protos_dot_ydb__auth__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='ydb/public/api/grpc/ydb_auth_v1.proto',
  package='Ydb.Auth.V1',
  syntax='proto3',
  serialized_options=b'\n\026com.yandex.ydb.auth.v1',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n%ydb/public/api/grpc/ydb_auth_v1.proto\x12\x0bYdb.Auth.V1\x1a$ydb/public/api/protos/ydb_auth.proto2G\n\x0b\x41uthService\x12\x38\n\x05Login\x12\x16.Ydb.Auth.LoginRequest\x1a\x17.Ydb.Auth.LoginResponseB\x18\n\x16\x63om.yandex.ydb.auth.v1b\x06proto3'
  ,
  dependencies=[ydb_dot_public_dot_api_dot_protos_dot_ydb__auth__pb2.DESCRIPTOR,])



_sym_db.RegisterFileDescriptor(DESCRIPTOR)


DESCRIPTOR._options = None

_AUTHSERVICE = _descriptor.ServiceDescriptor(
  name='AuthService',
  full_name='Ydb.Auth.V1.AuthService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=92,
  serialized_end=163,
  methods=[
  _descriptor.MethodDescriptor(
    name='Login',
    full_name='Ydb.Auth.V1.AuthService.Login',
    index=0,
    containing_service=None,
    input_type=ydb_dot_public_dot_api_dot_protos_dot_ydb__auth__pb2._LOGINREQUEST,
    output_type=ydb_dot_public_dot_api_dot_protos_dot_ydb__auth__pb2._LOGINRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_AUTHSERVICE)

DESCRIPTOR.services_by_name['AuthService'] = _AUTHSERVICE

# @@protoc_insertion_point(module_scope)

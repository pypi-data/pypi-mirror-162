# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ydb/public/api/protos/draft/persqueue_common.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2
from ydb.public.api.protos.draft import persqueue_error_codes_pb2 as ydb_dot_public_dot_api_dot_protos_dot_draft_dot_persqueue__error__codes__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='ydb/public/api/protos/draft/persqueue_common.proto',
  package='NPersQueueCommon',
  syntax='proto3',
  serialized_options=b'\n\030com.yandex.ydb.persqueue\370\001\001',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n2ydb/public/api/protos/draft/persqueue_common.proto\x12\x10NPersQueueCommon\x1a google/protobuf/descriptor.proto\x1a\x37ydb/public/api/protos/draft/persqueue_error_codes.proto\"M\n\x05\x45rror\x12/\n\x04\x63ode\x18\x01 \x01(\x0e\x32!.NPersQueue.NErrorCode.EErrorCode\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\"Q\n\x0b\x43redentials\x12\x1c\n\x12tvm_service_ticket\x18\x01 \x01(\x0cH\x00\x12\x15\n\x0boauth_token\x18\x02 \x01(\x0cH\x00\x42\r\n\x0b\x63redentials*<\n\x06\x45\x43odec\x12\x07\n\x03RAW\x10\x00\x12\x08\n\x04GZIP\x10\x01\x12\x08\n\x04LZOP\x10\x02\x12\x08\n\x04ZSTD\x10\x03\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x64:7\n\x0fGenerateYaStyle\x12\x1c.google.protobuf.FileOptions\x18\xf6\x88\x04 \x01(\x08\x42\x1d\n\x18\x63om.yandex.ydb.persqueue\xf8\x01\x01\x62\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_descriptor__pb2.DESCRIPTOR,ydb_dot_public_dot_api_dot_protos_dot_draft_dot_persqueue__error__codes__pb2.DESCRIPTOR,])

_ECODEC = _descriptor.EnumDescriptor(
  name='ECodec',
  full_name='NPersQueueCommon.ECodec',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='RAW', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='GZIP', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='LZOP', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='ZSTD', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DEFAULT', index=4, number=100,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=325,
  serialized_end=385,
)
_sym_db.RegisterEnumDescriptor(_ECODEC)

ECodec = enum_type_wrapper.EnumTypeWrapper(_ECODEC)
RAW = 0
GZIP = 1
LZOP = 2
ZSTD = 3
DEFAULT = 100

GENERATEYASTYLE_FIELD_NUMBER = 66678
GenerateYaStyle = _descriptor.FieldDescriptor(
  name='GenerateYaStyle', full_name='NPersQueueCommon.GenerateYaStyle', index=0,
  number=66678, type=8, cpp_type=7, label=1,
  has_default_value=False, default_value=False,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key)


_ERROR = _descriptor.Descriptor(
  name='Error',
  full_name='NPersQueueCommon.Error',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='code', full_name='NPersQueueCommon.Error.code', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='description', full_name='NPersQueueCommon.Error.description', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=163,
  serialized_end=240,
)


_CREDENTIALS = _descriptor.Descriptor(
  name='Credentials',
  full_name='NPersQueueCommon.Credentials',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='tvm_service_ticket', full_name='NPersQueueCommon.Credentials.tvm_service_ticket', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='oauth_token', full_name='NPersQueueCommon.Credentials.oauth_token', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='credentials', full_name='NPersQueueCommon.Credentials.credentials',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=242,
  serialized_end=323,
)

_ERROR.fields_by_name['code'].enum_type = ydb_dot_public_dot_api_dot_protos_dot_draft_dot_persqueue__error__codes__pb2._EERRORCODE
_CREDENTIALS.oneofs_by_name['credentials'].fields.append(
  _CREDENTIALS.fields_by_name['tvm_service_ticket'])
_CREDENTIALS.fields_by_name['tvm_service_ticket'].containing_oneof = _CREDENTIALS.oneofs_by_name['credentials']
_CREDENTIALS.oneofs_by_name['credentials'].fields.append(
  _CREDENTIALS.fields_by_name['oauth_token'])
_CREDENTIALS.fields_by_name['oauth_token'].containing_oneof = _CREDENTIALS.oneofs_by_name['credentials']
DESCRIPTOR.message_types_by_name['Error'] = _ERROR
DESCRIPTOR.message_types_by_name['Credentials'] = _CREDENTIALS
DESCRIPTOR.enum_types_by_name['ECodec'] = _ECODEC
DESCRIPTOR.extensions_by_name['GenerateYaStyle'] = GenerateYaStyle
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Error = _reflection.GeneratedProtocolMessageType('Error', (_message.Message,), {
  'DESCRIPTOR' : _ERROR,
  '__module__' : 'ydb.public.api.protos.draft.persqueue_common_pb2'
  # @@protoc_insertion_point(class_scope:NPersQueueCommon.Error)
  })
_sym_db.RegisterMessage(Error)

Credentials = _reflection.GeneratedProtocolMessageType('Credentials', (_message.Message,), {
  'DESCRIPTOR' : _CREDENTIALS,
  '__module__' : 'ydb.public.api.protos.draft.persqueue_common_pb2'
  # @@protoc_insertion_point(class_scope:NPersQueueCommon.Credentials)
  })
_sym_db.RegisterMessage(Credentials)

google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(GenerateYaStyle)

DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)

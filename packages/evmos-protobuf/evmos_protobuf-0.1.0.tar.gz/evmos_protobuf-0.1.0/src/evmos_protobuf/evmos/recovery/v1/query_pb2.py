
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from ....evmos.recovery.v1 import genesis_pb2 as evmos_dot_recovery_dot_v1_dot_genesis__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1devmos/recovery/v1/query.proto\x12\x11evmos.recovery.v1\x1a\x1cgoogle/api/annotations.proto\x1a\x14gogoproto/gogo.proto\x1a\x1fevmos/recovery/v1/genesis.proto"\x14\n\x12QueryParamsRequest"F\n\x13QueryParamsResponse\x12/\n\x06params\x18\x01 \x01(\x0b2\x19.evmos.recovery.v1.ParamsB\x04\xc8\xde\x1f\x002\x83\x01\n\x05Query\x12z\n\x06Params\x12%.evmos.recovery.v1.QueryParamsRequest\x1a&.evmos.recovery.v1.QueryParamsResponse"!\x82\xd3\xe4\x93\x02\x1b\x12\x19/evmos/recovery/v1/paramsB,Z*github.com/evmos/evmos/v7/x/recovery/typesb\x06proto3')
_QUERYPARAMSREQUEST = DESCRIPTOR.message_types_by_name['QueryParamsRequest']
_QUERYPARAMSRESPONSE = DESCRIPTOR.message_types_by_name['QueryParamsResponse']
QueryParamsRequest = _reflection.GeneratedProtocolMessageType('QueryParamsRequest', (_message.Message,), {'DESCRIPTOR': _QUERYPARAMSREQUEST, '__module__': 'evmos.recovery.v1.query_pb2'})
_sym_db.RegisterMessage(QueryParamsRequest)
QueryParamsResponse = _reflection.GeneratedProtocolMessageType('QueryParamsResponse', (_message.Message,), {'DESCRIPTOR': _QUERYPARAMSRESPONSE, '__module__': 'evmos.recovery.v1.query_pb2'})
_sym_db.RegisterMessage(QueryParamsResponse)
_QUERY = DESCRIPTOR.services_by_name['Query']
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z*github.com/evmos/evmos/v7/x/recovery/types'
    _QUERYPARAMSRESPONSE.fields_by_name['params']._options = None
    _QUERYPARAMSRESPONSE.fields_by_name['params']._serialized_options = b'\xc8\xde\x1f\x00'
    _QUERY.methods_by_name['Params']._options = None
    _QUERY.methods_by_name['Params']._serialized_options = b'\x82\xd3\xe4\x93\x02\x1b\x12\x19/evmos/recovery/v1/params'
    _QUERYPARAMSREQUEST._serialized_start = 137
    _QUERYPARAMSREQUEST._serialized_end = 157
    _QUERYPARAMSRESPONSE._serialized_start = 159
    _QUERYPARAMSRESPONSE._serialized_end = 229
    _QUERY._serialized_start = 232
    _QUERY._serialized_end = 363

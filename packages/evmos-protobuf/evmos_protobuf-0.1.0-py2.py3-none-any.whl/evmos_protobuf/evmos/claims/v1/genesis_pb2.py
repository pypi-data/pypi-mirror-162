
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from ....evmos.claims.v1 import claims_pb2 as evmos_dot_claims_dot_v1_dot_claims__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1devmos/claims/v1/genesis.proto\x12\x0fevmos.claims.v1\x1a\x14gogoproto/gogo.proto\x1a\x1egoogle/protobuf/duration.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1cevmos/claims/v1/claims.proto"\x81\x01\n\x0cGenesisState\x12-\n\x06params\x18\x01 \x01(\x0b2\x17.evmos.claims.v1.ParamsB\x04\xc8\xde\x1f\x00\x12B\n\x0eclaims_records\x18\x02 \x03(\x0b2$.evmos.claims.v1.ClaimsRecordAddressB\x04\xc8\xde\x1f\x00"\xbe\x02\n\x06Params\x12\x15\n\renable_claims\x18\x01 \x01(\x08\x12@\n\x12airdrop_start_time\x18\x02 \x01(\x0b2\x1a.google.protobuf.TimestampB\x08\xc8\xde\x1f\x00\x90\xdf\x1f\x01\x12A\n\x14duration_until_decay\x18\x03 \x01(\x0b2\x19.google.protobuf.DurationB\x08\xc8\xde\x1f\x00\x98\xdf\x1f\x01\x12>\n\x11duration_of_decay\x18\x04 \x01(\x0b2\x19.google.protobuf.DurationB\x08\xc8\xde\x1f\x00\x98\xdf\x1f\x01\x12\x14\n\x0cclaims_denom\x18\x05 \x01(\t\x12\x1b\n\x13authorized_channels\x18\x06 \x03(\t\x12%\n\x0cevm_channels\x18\x07 \x03(\tB\x0f\xe2\xde\x1f\x0bEVMChannelsB*Z(github.com/evmos/evmos/v7/x/claims/typesb\x06proto3')
_GENESISSTATE = DESCRIPTOR.message_types_by_name['GenesisState']
_PARAMS = DESCRIPTOR.message_types_by_name['Params']
GenesisState = _reflection.GeneratedProtocolMessageType('GenesisState', (_message.Message,), {'DESCRIPTOR': _GENESISSTATE, '__module__': 'evmos.claims.v1.genesis_pb2'})
_sym_db.RegisterMessage(GenesisState)
Params = _reflection.GeneratedProtocolMessageType('Params', (_message.Message,), {'DESCRIPTOR': _PARAMS, '__module__': 'evmos.claims.v1.genesis_pb2'})
_sym_db.RegisterMessage(Params)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z(github.com/evmos/evmos/v7/x/claims/types'
    _GENESISSTATE.fields_by_name['params']._options = None
    _GENESISSTATE.fields_by_name['params']._serialized_options = b'\xc8\xde\x1f\x00'
    _GENESISSTATE.fields_by_name['claims_records']._options = None
    _GENESISSTATE.fields_by_name['claims_records']._serialized_options = b'\xc8\xde\x1f\x00'
    _PARAMS.fields_by_name['airdrop_start_time']._options = None
    _PARAMS.fields_by_name['airdrop_start_time']._serialized_options = b'\xc8\xde\x1f\x00\x90\xdf\x1f\x01'
    _PARAMS.fields_by_name['duration_until_decay']._options = None
    _PARAMS.fields_by_name['duration_until_decay']._serialized_options = b'\xc8\xde\x1f\x00\x98\xdf\x1f\x01'
    _PARAMS.fields_by_name['duration_of_decay']._options = None
    _PARAMS.fields_by_name['duration_of_decay']._serialized_options = b'\xc8\xde\x1f\x00\x98\xdf\x1f\x01'
    _PARAMS.fields_by_name['evm_channels']._options = None
    _PARAMS.fields_by_name['evm_channels']._serialized_options = b'\xe2\xde\x1f\x0bEVMChannels'
    _GENESISSTATE._serialized_start = 168
    _GENESISSTATE._serialized_end = 297
    _PARAMS._serialized_start = 300
    _PARAMS._serialized_end = 618

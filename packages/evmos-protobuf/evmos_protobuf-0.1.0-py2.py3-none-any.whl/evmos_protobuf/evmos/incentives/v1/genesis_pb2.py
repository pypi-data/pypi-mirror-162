
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....evmos.incentives.v1 import incentives_pb2 as evmos_dot_incentives_dot_v1_dot_incentives__pb2
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!evmos/incentives/v1/genesis.proto\x12\x13evmos.incentives.v1\x1a$evmos/incentives/v1/incentives.proto\x1a\x14gogoproto/gogo.proto"\xb4\x01\n\x0cGenesisState\x121\n\x06params\x18\x01 \x01(\x0b2\x1b.evmos.incentives.v1.ParamsB\x04\xc8\xde\x1f\x00\x128\n\nincentives\x18\x02 \x03(\x0b2\x1e.evmos.incentives.v1.IncentiveB\x04\xc8\xde\x1f\x00\x127\n\ngas_meters\x18\x03 \x03(\x0b2\x1d.evmos.incentives.v1.GasMeterB\x04\xc8\xde\x1f\x00"\xd9\x01\n\x06Params\x12\x19\n\x11enable_incentives\x18\x01 \x01(\x08\x12H\n\x10allocation_limit\x18\x02 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\x12#\n\x1bincentives_epoch_identifier\x18\x03 \x01(\t\x12E\n\rreward_scaler\x18\x04 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00B.Z,github.com/evmos/evmos/v7/x/incentives/typesb\x06proto3')
_GENESISSTATE = DESCRIPTOR.message_types_by_name['GenesisState']
_PARAMS = DESCRIPTOR.message_types_by_name['Params']
GenesisState = _reflection.GeneratedProtocolMessageType('GenesisState', (_message.Message,), {'DESCRIPTOR': _GENESISSTATE, '__module__': 'evmos.incentives.v1.genesis_pb2'})
_sym_db.RegisterMessage(GenesisState)
Params = _reflection.GeneratedProtocolMessageType('Params', (_message.Message,), {'DESCRIPTOR': _PARAMS, '__module__': 'evmos.incentives.v1.genesis_pb2'})
_sym_db.RegisterMessage(Params)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z,github.com/evmos/evmos/v7/x/incentives/types'
    _GENESISSTATE.fields_by_name['params']._options = None
    _GENESISSTATE.fields_by_name['params']._serialized_options = b'\xc8\xde\x1f\x00'
    _GENESISSTATE.fields_by_name['incentives']._options = None
    _GENESISSTATE.fields_by_name['incentives']._serialized_options = b'\xc8\xde\x1f\x00'
    _GENESISSTATE.fields_by_name['gas_meters']._options = None
    _GENESISSTATE.fields_by_name['gas_meters']._serialized_options = b'\xc8\xde\x1f\x00'
    _PARAMS.fields_by_name['allocation_limit']._options = None
    _PARAMS.fields_by_name['allocation_limit']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _PARAMS.fields_by_name['reward_scaler']._options = None
    _PARAMS.fields_by_name['reward_scaler']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _GENESISSTATE._serialized_start = 119
    _GENESISSTATE._serialized_end = 299
    _PARAMS._serialized_start = 302
    _PARAMS._serialized_end = 519


'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from ....evmos.inflation.v1 import inflation_pb2 as evmos_dot_inflation_dot_v1_dot_inflation__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n evmos/inflation/v1/genesis.proto\x12\x12evmos.inflation.v1\x1a\x14gogoproto/gogo.proto\x1a"evmos/inflation/v1/inflation.proto"\x9d\x01\n\x0cGenesisState\x120\n\x06params\x18\x01 \x01(\x0b2\x1a.evmos.inflation.v1.ParamsB\x04\xc8\xde\x1f\x00\x12\x0e\n\x06period\x18\x02 \x01(\x04\x12\x18\n\x10epoch_identifier\x18\x03 \x01(\t\x12\x19\n\x11epochs_per_period\x18\x04 \x01(\x03\x12\x16\n\x0eskipped_epochs\x18\x05 \x01(\x04"\xda\x01\n\x06Params\x12\x12\n\nmint_denom\x18\x01 \x01(\t\x12Q\n\x17exponential_calculation\x18\x02 \x01(\x0b2*.evmos.inflation.v1.ExponentialCalculationB\x04\xc8\xde\x1f\x00\x12O\n\x16inflation_distribution\x18\x03 \x01(\x0b2).evmos.inflation.v1.InflationDistributionB\x04\xc8\xde\x1f\x00\x12\x18\n\x10enable_inflation\x18\x04 \x01(\x08B-Z+github.com/evmos/evmos/v7/x/inflation/typesb\x06proto3')
_GENESISSTATE = DESCRIPTOR.message_types_by_name['GenesisState']
_PARAMS = DESCRIPTOR.message_types_by_name['Params']
GenesisState = _reflection.GeneratedProtocolMessageType('GenesisState', (_message.Message,), {'DESCRIPTOR': _GENESISSTATE, '__module__': 'evmos.inflation.v1.genesis_pb2'})
_sym_db.RegisterMessage(GenesisState)
Params = _reflection.GeneratedProtocolMessageType('Params', (_message.Message,), {'DESCRIPTOR': _PARAMS, '__module__': 'evmos.inflation.v1.genesis_pb2'})
_sym_db.RegisterMessage(Params)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z+github.com/evmos/evmos/v7/x/inflation/types'
    _GENESISSTATE.fields_by_name['params']._options = None
    _GENESISSTATE.fields_by_name['params']._serialized_options = b'\xc8\xde\x1f\x00'
    _PARAMS.fields_by_name['exponential_calculation']._options = None
    _PARAMS.fields_by_name['exponential_calculation']._serialized_options = b'\xc8\xde\x1f\x00'
    _PARAMS.fields_by_name['inflation_distribution']._options = None
    _PARAMS.fields_by_name['inflation_distribution']._serialized_options = b'\xc8\xde\x1f\x00'
    _GENESISSTATE._serialized_start = 115
    _GENESISSTATE._serialized_end = 272
    _PARAMS._serialized_start = 275
    _PARAMS._serialized_end = 493


'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....evmos.erc20.v1 import erc20_pb2 as evmos_dot_erc20_dot_v1_dot_erc20__pb2
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1cevmos/erc20/v1/genesis.proto\x12\x0eevmos.erc20.v1\x1a\x1aevmos/erc20/v1/erc20.proto\x1a\x14gogoproto/gogo.proto"r\n\x0cGenesisState\x12,\n\x06params\x18\x01 \x01(\x0b2\x16.evmos.erc20.v1.ParamsB\x04\xc8\xde\x1f\x00\x124\n\x0btoken_pairs\x18\x02 \x03(\x0b2\x19.evmos.erc20.v1.TokenPairB\x04\xc8\xde\x1f\x00"J\n\x06Params\x12\x14\n\x0cenable_erc20\x18\x01 \x01(\x08\x12*\n\x0fenable_evm_hook\x18\x02 \x01(\x08B\x11\xe2\xde\x1f\rEnableEVMHookB)Z\'github.com/evmos/evmos/v7/x/erc20/typesb\x06proto3')
_GENESISSTATE = DESCRIPTOR.message_types_by_name['GenesisState']
_PARAMS = DESCRIPTOR.message_types_by_name['Params']
GenesisState = _reflection.GeneratedProtocolMessageType('GenesisState', (_message.Message,), {'DESCRIPTOR': _GENESISSTATE, '__module__': 'evmos.erc20.v1.genesis_pb2'})
_sym_db.RegisterMessage(GenesisState)
Params = _reflection.GeneratedProtocolMessageType('Params', (_message.Message,), {'DESCRIPTOR': _PARAMS, '__module__': 'evmos.erc20.v1.genesis_pb2'})
_sym_db.RegisterMessage(Params)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z'github.com/evmos/evmos/v7/x/erc20/types"
    _GENESISSTATE.fields_by_name['params']._options = None
    _GENESISSTATE.fields_by_name['params']._serialized_options = b'\xc8\xde\x1f\x00'
    _GENESISSTATE.fields_by_name['token_pairs']._options = None
    _GENESISSTATE.fields_by_name['token_pairs']._serialized_options = b'\xc8\xde\x1f\x00'
    _PARAMS.fields_by_name['enable_evm_hook']._options = None
    _PARAMS.fields_by_name['enable_evm_hook']._serialized_options = b'\xe2\xde\x1f\rEnableEVMHook'
    _GENESISSTATE._serialized_start = 98
    _GENESISSTATE._serialized_end = 212
    _PARAMS._serialized_start = 214
    _PARAMS._serialized_end = 288

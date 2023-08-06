
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from ....ethermint.evm.v1 import evm_pb2 as ethermint_dot_evm_dot_v1_dot_evm__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eethermint/evm/v1/genesis.proto\x12\x10ethermint.evm.v1\x1a\x14gogoproto/gogo.proto\x1a\x1aethermint/evm/v1/evm.proto"x\n\x0cGenesisState\x128\n\x08accounts\x18\x01 \x03(\x0b2 .ethermint.evm.v1.GenesisAccountB\x04\xc8\xde\x1f\x00\x12.\n\x06params\x18\x02 \x01(\x0b2\x18.ethermint.evm.v1.ParamsB\x04\xc8\xde\x1f\x00"j\n\x0eGenesisAccount\x12\x0f\n\x07address\x18\x01 \x01(\t\x12\x0c\n\x04code\x18\x02 \x01(\t\x129\n\x07storage\x18\x03 \x03(\x0b2\x17.ethermint.evm.v1.StateB\x0f\xc8\xde\x1f\x00\xaa\xdf\x1f\x07StorageB(Z&github.com/evmos/ethermint/x/evm/typesb\x06proto3')
_GENESISSTATE = DESCRIPTOR.message_types_by_name['GenesisState']
_GENESISACCOUNT = DESCRIPTOR.message_types_by_name['GenesisAccount']
GenesisState = _reflection.GeneratedProtocolMessageType('GenesisState', (_message.Message,), {'DESCRIPTOR': _GENESISSTATE, '__module__': 'ethermint.evm.v1.genesis_pb2'})
_sym_db.RegisterMessage(GenesisState)
GenesisAccount = _reflection.GeneratedProtocolMessageType('GenesisAccount', (_message.Message,), {'DESCRIPTOR': _GENESISACCOUNT, '__module__': 'ethermint.evm.v1.genesis_pb2'})
_sym_db.RegisterMessage(GenesisAccount)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z&github.com/evmos/ethermint/x/evm/types'
    _GENESISSTATE.fields_by_name['accounts']._options = None
    _GENESISSTATE.fields_by_name['accounts']._serialized_options = b'\xc8\xde\x1f\x00'
    _GENESISSTATE.fields_by_name['params']._options = None
    _GENESISSTATE.fields_by_name['params']._serialized_options = b'\xc8\xde\x1f\x00'
    _GENESISACCOUNT.fields_by_name['storage']._options = None
    _GENESISACCOUNT.fields_by_name['storage']._serialized_options = b'\xc8\xde\x1f\x00\xaa\xdf\x1f\x07Storage'
    _GENESISSTATE._serialized_start = 102
    _GENESISSTATE._serialized_end = 222
    _GENESISACCOUNT._serialized_start = 224
    _GENESISACCOUNT._serialized_end = 330


'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....cosmos.auth.v1beta1 import auth_pb2 as cosmos_dot_auth_dot_v1beta1_dot_auth__pb2
from ....cosmos_proto import cosmos_pb2 as cosmos__proto_dot_cosmos__pb2
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n ethermint/types/v1/account.proto\x12\x12ethermint.types.v1\x1a\x1ecosmos/auth/v1beta1/auth.proto\x1a\x19cosmos_proto/cosmos.proto\x1a\x14gogoproto/gogo.proto"\xce\x01\n\nEthAccount\x12S\n\x0cbase_account\x18\x01 \x01(\x0b2 .cosmos.auth.v1beta1.BaseAccountB\x1b\xd0\xde\x1f\x01\xf2\xde\x1f\x13yaml:"base_account"\x12\'\n\tcode_hash\x18\x02 \x01(\tB\x14\xf2\xde\x1f\x10yaml:"code_hash":B\x88\xa0\x1f\x00\x98\xa0\x1f\x00\xe8\xa0\x1f\x00\xca\xb4-2github.com/cosmos/cosmos-sdk/x/auth/types.AccountIB"Z github.com/evmos/ethermint/typesb\x06proto3')
_ETHACCOUNT = DESCRIPTOR.message_types_by_name['EthAccount']
EthAccount = _reflection.GeneratedProtocolMessageType('EthAccount', (_message.Message,), {'DESCRIPTOR': _ETHACCOUNT, '__module__': 'ethermint.types.v1.account_pb2'})
_sym_db.RegisterMessage(EthAccount)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z github.com/evmos/ethermint/types'
    _ETHACCOUNT.fields_by_name['base_account']._options = None
    _ETHACCOUNT.fields_by_name['base_account']._serialized_options = b'\xd0\xde\x1f\x01\xf2\xde\x1f\x13yaml:"base_account"'
    _ETHACCOUNT.fields_by_name['code_hash']._options = None
    _ETHACCOUNT.fields_by_name['code_hash']._serialized_options = b'\xf2\xde\x1f\x10yaml:"code_hash"'
    _ETHACCOUNT._options = None
    _ETHACCOUNT._serialized_options = b'\x88\xa0\x1f\x00\x98\xa0\x1f\x00\xe8\xa0\x1f\x00\xca\xb4-2github.com/cosmos/cosmos-sdk/x/auth/types.AccountI'
    _ETHACCOUNT._serialized_start = 138
    _ETHACCOUNT._serialized_end = 344

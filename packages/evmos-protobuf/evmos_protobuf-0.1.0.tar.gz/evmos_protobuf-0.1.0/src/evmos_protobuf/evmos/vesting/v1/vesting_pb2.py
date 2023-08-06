
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from ....cosmos.vesting.v1beta1 import vesting_pb2 as cosmos_dot_vesting_dot_v1beta1_dot_vesting__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eevmos/vesting/v1/vesting.proto\x12\x10evmos.vesting.v1\x1a\x14gogoproto/gogo.proto\x1a$cosmos/vesting/v1beta1/vesting.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\xbb\x03\n\x16ClawbackVestingAccount\x12N\n\x14base_vesting_account\x18\x01 \x01(\x0b2*.cosmos.vesting.v1beta1.BaseVestingAccountB\x04\xd0\xde\x1f\x01\x12\x16\n\x0efunder_address\x18\x02 \x01(\t\x128\n\nstart_time\x18\x03 \x01(\x0b2\x1a.google.protobuf.TimestampB\x08\x90\xdf\x1f\x01\xc8\xde\x1f\x00\x12y\n\x0elockup_periods\x18\x04 \x03(\x0b2\x1e.cosmos.vesting.v1beta1.PeriodBA\xc8\xde\x1f\x00\xaa\xdf\x1f9github.com/cosmos/cosmos-sdk/x/auth/vesting/types.Periods\x12z\n\x0fvesting_periods\x18\x05 \x03(\x0b2\x1e.cosmos.vesting.v1beta1.PeriodBA\xc8\xde\x1f\x00\xaa\xdf\x1f9github.com/cosmos/cosmos-sdk/x/auth/vesting/types.Periods:\x08\x88\xa0\x1f\x00\x98\xa0\x1f\x00B+Z)github.com/evmos/evmos/v7/x/vesting/typesb\x06proto3')
_CLAWBACKVESTINGACCOUNT = DESCRIPTOR.message_types_by_name['ClawbackVestingAccount']
ClawbackVestingAccount = _reflection.GeneratedProtocolMessageType('ClawbackVestingAccount', (_message.Message,), {'DESCRIPTOR': _CLAWBACKVESTINGACCOUNT, '__module__': 'evmos.vesting.v1.vesting_pb2'})
_sym_db.RegisterMessage(ClawbackVestingAccount)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z)github.com/evmos/evmos/v7/x/vesting/types'
    _CLAWBACKVESTINGACCOUNT.fields_by_name['base_vesting_account']._options = None
    _CLAWBACKVESTINGACCOUNT.fields_by_name['base_vesting_account']._serialized_options = b'\xd0\xde\x1f\x01'
    _CLAWBACKVESTINGACCOUNT.fields_by_name['start_time']._options = None
    _CLAWBACKVESTINGACCOUNT.fields_by_name['start_time']._serialized_options = b'\x90\xdf\x1f\x01\xc8\xde\x1f\x00'
    _CLAWBACKVESTINGACCOUNT.fields_by_name['lockup_periods']._options = None
    _CLAWBACKVESTINGACCOUNT.fields_by_name['lockup_periods']._serialized_options = b'\xc8\xde\x1f\x00\xaa\xdf\x1f9github.com/cosmos/cosmos-sdk/x/auth/vesting/types.Periods'
    _CLAWBACKVESTINGACCOUNT.fields_by_name['vesting_periods']._options = None
    _CLAWBACKVESTINGACCOUNT.fields_by_name['vesting_periods']._serialized_options = b'\xc8\xde\x1f\x00\xaa\xdf\x1f9github.com/cosmos/cosmos-sdk/x/auth/vesting/types.Periods'
    _CLAWBACKVESTINGACCOUNT._options = None
    _CLAWBACKVESTINGACCOUNT._serialized_options = b'\x88\xa0\x1f\x00\x98\xa0\x1f\x00'
    _CLAWBACKVESTINGACCOUNT._serialized_start = 146
    _CLAWBACKVESTINGACCOUNT._serialized_end = 589

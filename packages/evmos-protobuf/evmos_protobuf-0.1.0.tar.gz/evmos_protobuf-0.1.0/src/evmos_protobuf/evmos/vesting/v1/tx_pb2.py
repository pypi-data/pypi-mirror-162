
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from ....cosmos.vesting.v1beta1 import vesting_pb2 as cosmos_dot_vesting_dot_v1beta1_dot_vesting__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19evmos/vesting/v1/tx.proto\x12\x10evmos.vesting.v1\x1a\x1cgoogle/api/annotations.proto\x1a\x14gogoproto/gogo.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a$cosmos/vesting/v1beta1/vesting.proto"\x91\x03\n\x1fMsgCreateClawbackVestingAccount\x12\x14\n\x0cfrom_address\x18\x01 \x01(\t\x12\x12\n\nto_address\x18\x02 \x01(\t\x128\n\nstart_time\x18\x03 \x01(\x0b2\x1a.google.protobuf.TimestampB\x08\x90\xdf\x1f\x01\xc8\xde\x1f\x00\x12y\n\x0elockup_periods\x18\x04 \x03(\x0b2\x1e.cosmos.vesting.v1beta1.PeriodBA\xc8\xde\x1f\x00\xaa\xdf\x1f9github.com/cosmos/cosmos-sdk/x/auth/vesting/types.Periods\x12z\n\x0fvesting_periods\x18\x05 \x03(\x0b2\x1e.cosmos.vesting.v1beta1.PeriodBA\xc8\xde\x1f\x00\xaa\xdf\x1f9github.com/cosmos/cosmos-sdk/x/auth/vesting/types.Periods\x12\r\n\x05merge\x18\x06 \x01(\x08:\x04\xe8\xa0\x1f\x00")\n\'MsgCreateClawbackVestingAccountResponse"T\n\x0bMsgClawback\x12\x16\n\x0efunder_address\x18\x01 \x01(\t\x12\x17\n\x0faccount_address\x18\x02 \x01(\t\x12\x14\n\x0cdest_address\x18\x03 \x01(\t"\x15\n\x13MsgClawbackResponse2\xcb\x02\n\x03Msg\x12\xca\x01\n\x1cCreateClawbackVestingAccount\x121.evmos.vesting.v1.MsgCreateClawbackVestingAccount\x1a9.evmos.vesting.v1.MsgCreateClawbackVestingAccountResponse"<\x82\xd3\xe4\x93\x026\x124/evmos/vesting/v1/tx/create_clawback_vesting_account\x12w\n\x08Clawback\x12\x1d.evmos.vesting.v1.MsgClawback\x1a%.evmos.vesting.v1.MsgClawbackResponse"%\x82\xd3\xe4\x93\x02\x1f\x12\x1d/evmos/vesting/v1/tx/clawbackB+Z)github.com/evmos/evmos/v7/x/vesting/typesb\x06proto3')
_MSGCREATECLAWBACKVESTINGACCOUNT = DESCRIPTOR.message_types_by_name['MsgCreateClawbackVestingAccount']
_MSGCREATECLAWBACKVESTINGACCOUNTRESPONSE = DESCRIPTOR.message_types_by_name['MsgCreateClawbackVestingAccountResponse']
_MSGCLAWBACK = DESCRIPTOR.message_types_by_name['MsgClawback']
_MSGCLAWBACKRESPONSE = DESCRIPTOR.message_types_by_name['MsgClawbackResponse']
MsgCreateClawbackVestingAccount = _reflection.GeneratedProtocolMessageType('MsgCreateClawbackVestingAccount', (_message.Message,), {'DESCRIPTOR': _MSGCREATECLAWBACKVESTINGACCOUNT, '__module__': 'evmos.vesting.v1.tx_pb2'})
_sym_db.RegisterMessage(MsgCreateClawbackVestingAccount)
MsgCreateClawbackVestingAccountResponse = _reflection.GeneratedProtocolMessageType('MsgCreateClawbackVestingAccountResponse', (_message.Message,), {'DESCRIPTOR': _MSGCREATECLAWBACKVESTINGACCOUNTRESPONSE, '__module__': 'evmos.vesting.v1.tx_pb2'})
_sym_db.RegisterMessage(MsgCreateClawbackVestingAccountResponse)
MsgClawback = _reflection.GeneratedProtocolMessageType('MsgClawback', (_message.Message,), {'DESCRIPTOR': _MSGCLAWBACK, '__module__': 'evmos.vesting.v1.tx_pb2'})
_sym_db.RegisterMessage(MsgClawback)
MsgClawbackResponse = _reflection.GeneratedProtocolMessageType('MsgClawbackResponse', (_message.Message,), {'DESCRIPTOR': _MSGCLAWBACKRESPONSE, '__module__': 'evmos.vesting.v1.tx_pb2'})
_sym_db.RegisterMessage(MsgClawbackResponse)
_MSG = DESCRIPTOR.services_by_name['Msg']
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z)github.com/evmos/evmos/v7/x/vesting/types'
    _MSGCREATECLAWBACKVESTINGACCOUNT.fields_by_name['start_time']._options = None
    _MSGCREATECLAWBACKVESTINGACCOUNT.fields_by_name['start_time']._serialized_options = b'\x90\xdf\x1f\x01\xc8\xde\x1f\x00'
    _MSGCREATECLAWBACKVESTINGACCOUNT.fields_by_name['lockup_periods']._options = None
    _MSGCREATECLAWBACKVESTINGACCOUNT.fields_by_name['lockup_periods']._serialized_options = b'\xc8\xde\x1f\x00\xaa\xdf\x1f9github.com/cosmos/cosmos-sdk/x/auth/vesting/types.Periods'
    _MSGCREATECLAWBACKVESTINGACCOUNT.fields_by_name['vesting_periods']._options = None
    _MSGCREATECLAWBACKVESTINGACCOUNT.fields_by_name['vesting_periods']._serialized_options = b'\xc8\xde\x1f\x00\xaa\xdf\x1f9github.com/cosmos/cosmos-sdk/x/auth/vesting/types.Periods'
    _MSGCREATECLAWBACKVESTINGACCOUNT._options = None
    _MSGCREATECLAWBACKVESTINGACCOUNT._serialized_options = b'\xe8\xa0\x1f\x00'
    _MSG.methods_by_name['CreateClawbackVestingAccount']._options = None
    _MSG.methods_by_name['CreateClawbackVestingAccount']._serialized_options = b'\x82\xd3\xe4\x93\x026\x124/evmos/vesting/v1/tx/create_clawback_vesting_account'
    _MSG.methods_by_name['Clawback']._options = None
    _MSG.methods_by_name['Clawback']._serialized_options = b'\x82\xd3\xe4\x93\x02\x1f\x12\x1d/evmos/vesting/v1/tx/clawback'
    _MSGCREATECLAWBACKVESTINGACCOUNT._serialized_start = 171
    _MSGCREATECLAWBACKVESTINGACCOUNT._serialized_end = 572
    _MSGCREATECLAWBACKVESTINGACCOUNTRESPONSE._serialized_start = 574
    _MSGCREATECLAWBACKVESTINGACCOUNTRESPONSE._serialized_end = 615
    _MSGCLAWBACK._serialized_start = 617
    _MSGCLAWBACK._serialized_end = 701
    _MSGCLAWBACKRESPONSE._serialized_start = 703
    _MSGCLAWBACKRESPONSE._serialized_end = 724
    _MSG._serialized_start = 727
    _MSG._serialized_end = 1058

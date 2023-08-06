
'Generated protocol buffer code.'
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1cevmos/claims/v1/claims.proto\x12\x0fevmos.claims.v1\x1a\x14gogoproto/gogo.proto"\x8d\x01\n\x05Claim\x12\'\n\x06action\x18\x01 \x01(\x0e2\x17.evmos.claims.v1.Action\x12\x11\n\tcompleted\x18\x02 \x01(\x08\x12H\n\x10claimable_amount\x18\x03 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00"\x93\x01\n\x13ClaimsRecordAddress\x12\x0f\n\x07address\x18\x01 \x01(\t\x12P\n\x18initial_claimable_amount\x18\x02 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00\x12\x19\n\x11actions_completed\x18\x03 \x03(\x08"{\n\x0cClaimsRecord\x12P\n\x18initial_claimable_amount\x18\x01 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00\x12\x19\n\x11actions_completed\x18\x02 \x03(\x08*\xd6\x01\n\x06Action\x12-\n\x12ACTION_UNSPECIFIED\x10\x00\x1a\x15\x8a\x9d \x11ActionUnspecified\x12\x1f\n\x0bACTION_VOTE\x10\x01\x1a\x0e\x8a\x9d \nActionVote\x12\'\n\x0fACTION_DELEGATE\x10\x02\x1a\x12\x8a\x9d \x0eActionDelegate\x12\x1d\n\nACTION_EVM\x10\x03\x1a\r\x8a\x9d \tActionEVM\x12.\n\x13ACTION_IBC_TRANSFER\x10\x04\x1a\x15\x8a\x9d \x11ActionIBCTransfer\x1a\x04\x88\xa3\x1e\x00B*Z(github.com/evmos/evmos/v7/x/claims/typesb\x06proto3')
_ACTION = DESCRIPTOR.enum_types_by_name['Action']
Action = enum_type_wrapper.EnumTypeWrapper(_ACTION)
ACTION_UNSPECIFIED = 0
ACTION_VOTE = 1
ACTION_DELEGATE = 2
ACTION_EVM = 3
ACTION_IBC_TRANSFER = 4
_CLAIM = DESCRIPTOR.message_types_by_name['Claim']
_CLAIMSRECORDADDRESS = DESCRIPTOR.message_types_by_name['ClaimsRecordAddress']
_CLAIMSRECORD = DESCRIPTOR.message_types_by_name['ClaimsRecord']
Claim = _reflection.GeneratedProtocolMessageType('Claim', (_message.Message,), {'DESCRIPTOR': _CLAIM, '__module__': 'evmos.claims.v1.claims_pb2'})
_sym_db.RegisterMessage(Claim)
ClaimsRecordAddress = _reflection.GeneratedProtocolMessageType('ClaimsRecordAddress', (_message.Message,), {'DESCRIPTOR': _CLAIMSRECORDADDRESS, '__module__': 'evmos.claims.v1.claims_pb2'})
_sym_db.RegisterMessage(ClaimsRecordAddress)
ClaimsRecord = _reflection.GeneratedProtocolMessageType('ClaimsRecord', (_message.Message,), {'DESCRIPTOR': _CLAIMSRECORD, '__module__': 'evmos.claims.v1.claims_pb2'})
_sym_db.RegisterMessage(ClaimsRecord)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z(github.com/evmos/evmos/v7/x/claims/types'
    _ACTION._options = None
    _ACTION._serialized_options = b'\x88\xa3\x1e\x00'
    _ACTION.values_by_name['ACTION_UNSPECIFIED']._options = None
    _ACTION.values_by_name['ACTION_UNSPECIFIED']._serialized_options = b'\x8a\x9d \x11ActionUnspecified'
    _ACTION.values_by_name['ACTION_VOTE']._options = None
    _ACTION.values_by_name['ACTION_VOTE']._serialized_options = b'\x8a\x9d \nActionVote'
    _ACTION.values_by_name['ACTION_DELEGATE']._options = None
    _ACTION.values_by_name['ACTION_DELEGATE']._serialized_options = b'\x8a\x9d \x0eActionDelegate'
    _ACTION.values_by_name['ACTION_EVM']._options = None
    _ACTION.values_by_name['ACTION_EVM']._serialized_options = b'\x8a\x9d \tActionEVM'
    _ACTION.values_by_name['ACTION_IBC_TRANSFER']._options = None
    _ACTION.values_by_name['ACTION_IBC_TRANSFER']._serialized_options = b'\x8a\x9d \x11ActionIBCTransfer'
    _CLAIM.fields_by_name['claimable_amount']._options = None
    _CLAIM.fields_by_name['claimable_amount']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00'
    _CLAIMSRECORDADDRESS.fields_by_name['initial_claimable_amount']._options = None
    _CLAIMSRECORDADDRESS.fields_by_name['initial_claimable_amount']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00'
    _CLAIMSRECORD.fields_by_name['initial_claimable_amount']._options = None
    _CLAIMSRECORD.fields_by_name['initial_claimable_amount']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00'
    _ACTION._serialized_start = 491
    _ACTION._serialized_end = 705
    _CLAIM._serialized_start = 72
    _CLAIM._serialized_end = 213
    _CLAIMSRECORDADDRESS._serialized_start = 216
    _CLAIMSRECORDADDRESS._serialized_end = 363
    _CLAIMSRECORD._serialized_start = 365
    _CLAIMSRECORD._serialized_end = 488

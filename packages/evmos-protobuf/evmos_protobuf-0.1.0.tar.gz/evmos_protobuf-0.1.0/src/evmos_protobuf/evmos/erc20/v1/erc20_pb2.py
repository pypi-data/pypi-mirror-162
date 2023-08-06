
'Generated protocol buffer code.'
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from ....cosmos.bank.v1beta1 import bank_pb2 as cosmos_dot_bank_dot_v1beta1_dot_bank__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aevmos/erc20/v1/erc20.proto\x12\x0eevmos.erc20.v1\x1a\x14gogoproto/gogo.proto\x1a\x1ecosmos/bank/v1beta1/bank.proto"w\n\tTokenPair\x12\x15\n\rerc20_address\x18\x01 \x01(\t\x12\r\n\x05denom\x18\x02 \x01(\t\x12\x0f\n\x07enabled\x18\x03 \x01(\x08\x12-\n\x0econtract_owner\x18\x04 \x01(\x0e2\x15.evmos.erc20.v1.Owner:\x04\xe8\xa0\x1f\x01"w\n\x14RegisterCoinProposal\x12\r\n\x05title\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x125\n\x08metadata\x18\x03 \x01(\x0b2\x1d.cosmos.bank.v1beta1.MetadataB\x04\xc8\xde\x1f\x00:\x04\xe8\xa0\x1f\x00"W\n\x15RegisterERC20Proposal\x12\r\n\x05title\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x12\x14\n\x0cerc20address\x18\x03 \x01(\t:\x04\xe8\xa0\x1f\x00"X\n\x1dToggleTokenConversionProposal\x12\r\n\x05title\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x12\r\n\x05token\x18\x03 \x01(\t:\x04\xe8\xa0\x1f\x01*J\n\x05Owner\x12\x15\n\x11OWNER_UNSPECIFIED\x10\x00\x12\x10\n\x0cOWNER_MODULE\x10\x01\x12\x12\n\x0eOWNER_EXTERNAL\x10\x02\x1a\x04\x88\xa3\x1e\x00B)Z\'github.com/evmos/evmos/v7/x/erc20/typesb\x06proto3')
_OWNER = DESCRIPTOR.enum_types_by_name['Owner']
Owner = enum_type_wrapper.EnumTypeWrapper(_OWNER)
OWNER_UNSPECIFIED = 0
OWNER_MODULE = 1
OWNER_EXTERNAL = 2
_TOKENPAIR = DESCRIPTOR.message_types_by_name['TokenPair']
_REGISTERCOINPROPOSAL = DESCRIPTOR.message_types_by_name['RegisterCoinProposal']
_REGISTERERC20PROPOSAL = DESCRIPTOR.message_types_by_name['RegisterERC20Proposal']
_TOGGLETOKENCONVERSIONPROPOSAL = DESCRIPTOR.message_types_by_name['ToggleTokenConversionProposal']
TokenPair = _reflection.GeneratedProtocolMessageType('TokenPair', (_message.Message,), {'DESCRIPTOR': _TOKENPAIR, '__module__': 'evmos.erc20.v1.erc20_pb2'})
_sym_db.RegisterMessage(TokenPair)
RegisterCoinProposal = _reflection.GeneratedProtocolMessageType('RegisterCoinProposal', (_message.Message,), {'DESCRIPTOR': _REGISTERCOINPROPOSAL, '__module__': 'evmos.erc20.v1.erc20_pb2'})
_sym_db.RegisterMessage(RegisterCoinProposal)
RegisterERC20Proposal = _reflection.GeneratedProtocolMessageType('RegisterERC20Proposal', (_message.Message,), {'DESCRIPTOR': _REGISTERERC20PROPOSAL, '__module__': 'evmos.erc20.v1.erc20_pb2'})
_sym_db.RegisterMessage(RegisterERC20Proposal)
ToggleTokenConversionProposal = _reflection.GeneratedProtocolMessageType('ToggleTokenConversionProposal', (_message.Message,), {'DESCRIPTOR': _TOGGLETOKENCONVERSIONPROPOSAL, '__module__': 'evmos.erc20.v1.erc20_pb2'})
_sym_db.RegisterMessage(ToggleTokenConversionProposal)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z'github.com/evmos/evmos/v7/x/erc20/types"
    _OWNER._options = None
    _OWNER._serialized_options = b'\x88\xa3\x1e\x00'
    _TOKENPAIR._options = None
    _TOKENPAIR._serialized_options = b'\xe8\xa0\x1f\x01'
    _REGISTERCOINPROPOSAL.fields_by_name['metadata']._options = None
    _REGISTERCOINPROPOSAL.fields_by_name['metadata']._serialized_options = b'\xc8\xde\x1f\x00'
    _REGISTERCOINPROPOSAL._options = None
    _REGISTERCOINPROPOSAL._serialized_options = b'\xe8\xa0\x1f\x00'
    _REGISTERERC20PROPOSAL._options = None
    _REGISTERERC20PROPOSAL._serialized_options = b'\xe8\xa0\x1f\x00'
    _TOGGLETOKENCONVERSIONPROPOSAL._options = None
    _TOGGLETOKENCONVERSIONPROPOSAL._serialized_options = b'\xe8\xa0\x1f\x01'
    _OWNER._serialized_start = 521
    _OWNER._serialized_end = 595
    _TOKENPAIR._serialized_start = 100
    _TOKENPAIR._serialized_end = 219
    _REGISTERCOINPROPOSAL._serialized_start = 221
    _REGISTERCOINPROPOSAL._serialized_end = 340
    _REGISTERERC20PROPOSAL._serialized_start = 342
    _REGISTERERC20PROPOSAL._serialized_end = 429
    _TOGGLETOKENCONVERSIONPROPOSAL._serialized_start = 431
    _TOGGLETOKENCONVERSIONPROPOSAL._serialized_end = 519

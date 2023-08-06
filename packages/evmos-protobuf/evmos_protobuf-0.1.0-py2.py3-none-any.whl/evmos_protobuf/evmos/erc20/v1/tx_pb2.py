
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from ....cosmos.base.v1beta1 import coin_pb2 as cosmos_dot_base_dot_v1beta1_dot_coin__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17evmos/erc20/v1/tx.proto\x12\x0eevmos.erc20.v1\x1a\x1cgoogle/api/annotations.proto\x1a\x14gogoproto/gogo.proto\x1a\x1ecosmos/base/v1beta1/coin.proto"a\n\x0eMsgConvertCoin\x12-\n\x04coin\x18\x01 \x01(\x0b2\x19.cosmos.base.v1beta1.CoinB\x04\xc8\xde\x1f\x00\x12\x10\n\x08receiver\x18\x02 \x01(\t\x12\x0e\n\x06sender\x18\x03 \x01(\t"\x18\n\x16MsgConvertCoinResponse"\x8d\x01\n\x0fMsgConvertERC20\x12\x18\n\x10contract_address\x18\x01 \x01(\t\x12>\n\x06amount\x18\x02 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00\x12\x10\n\x08receiver\x18\x03 \x01(\t\x12\x0e\n\x06sender\x18\x04 \x01(\t"\x19\n\x17MsgConvertERC20Response2\x8a\x02\n\x03Msg\x12~\n\x0bConvertCoin\x12\x1e.evmos.erc20.v1.MsgConvertCoin\x1a&.evmos.erc20.v1.MsgConvertCoinResponse"\'\x82\xd3\xe4\x93\x02!\x12\x1f/evmos/erc20/v1/tx/convert_coin\x12\x82\x01\n\x0cConvertERC20\x12\x1f.evmos.erc20.v1.MsgConvertERC20\x1a\'.evmos.erc20.v1.MsgConvertERC20Response"(\x82\xd3\xe4\x93\x02"\x12 /evmos/erc20/v1/tx/convert_erc20B)Z\'github.com/evmos/evmos/v7/x/erc20/typesb\x06proto3')
_MSGCONVERTCOIN = DESCRIPTOR.message_types_by_name['MsgConvertCoin']
_MSGCONVERTCOINRESPONSE = DESCRIPTOR.message_types_by_name['MsgConvertCoinResponse']
_MSGCONVERTERC20 = DESCRIPTOR.message_types_by_name['MsgConvertERC20']
_MSGCONVERTERC20RESPONSE = DESCRIPTOR.message_types_by_name['MsgConvertERC20Response']
MsgConvertCoin = _reflection.GeneratedProtocolMessageType('MsgConvertCoin', (_message.Message,), {'DESCRIPTOR': _MSGCONVERTCOIN, '__module__': 'evmos.erc20.v1.tx_pb2'})
_sym_db.RegisterMessage(MsgConvertCoin)
MsgConvertCoinResponse = _reflection.GeneratedProtocolMessageType('MsgConvertCoinResponse', (_message.Message,), {'DESCRIPTOR': _MSGCONVERTCOINRESPONSE, '__module__': 'evmos.erc20.v1.tx_pb2'})
_sym_db.RegisterMessage(MsgConvertCoinResponse)
MsgConvertERC20 = _reflection.GeneratedProtocolMessageType('MsgConvertERC20', (_message.Message,), {'DESCRIPTOR': _MSGCONVERTERC20, '__module__': 'evmos.erc20.v1.tx_pb2'})
_sym_db.RegisterMessage(MsgConvertERC20)
MsgConvertERC20Response = _reflection.GeneratedProtocolMessageType('MsgConvertERC20Response', (_message.Message,), {'DESCRIPTOR': _MSGCONVERTERC20RESPONSE, '__module__': 'evmos.erc20.v1.tx_pb2'})
_sym_db.RegisterMessage(MsgConvertERC20Response)
_MSG = DESCRIPTOR.services_by_name['Msg']
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z'github.com/evmos/evmos/v7/x/erc20/types"
    _MSGCONVERTCOIN.fields_by_name['coin']._options = None
    _MSGCONVERTCOIN.fields_by_name['coin']._serialized_options = b'\xc8\xde\x1f\x00'
    _MSGCONVERTERC20.fields_by_name['amount']._options = None
    _MSGCONVERTERC20.fields_by_name['amount']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00'
    _MSG.methods_by_name['ConvertCoin']._options = None
    _MSG.methods_by_name['ConvertCoin']._serialized_options = b'\x82\xd3\xe4\x93\x02!\x12\x1f/evmos/erc20/v1/tx/convert_coin'
    _MSG.methods_by_name['ConvertERC20']._options = None
    _MSG.methods_by_name['ConvertERC20']._serialized_options = b'\x82\xd3\xe4\x93\x02"\x12 /evmos/erc20/v1/tx/convert_erc20'
    _MSGCONVERTCOIN._serialized_start = 127
    _MSGCONVERTCOIN._serialized_end = 224
    _MSGCONVERTCOINRESPONSE._serialized_start = 226
    _MSGCONVERTCOINRESPONSE._serialized_end = 250
    _MSGCONVERTERC20._serialized_start = 253
    _MSGCONVERTERC20._serialized_end = 394
    _MSGCONVERTERC20RESPONSE._serialized_start = 396
    _MSGCONVERTERC20RESPONSE._serialized_end = 421
    _MSG._serialized_start = 424
    _MSG._serialized_end = 690

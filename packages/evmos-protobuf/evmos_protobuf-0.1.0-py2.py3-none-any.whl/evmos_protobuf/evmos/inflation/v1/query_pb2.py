
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from ....google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from ....cosmos.base.v1beta1 import coin_pb2 as cosmos_dot_base_dot_v1beta1_dot_coin__pb2
from ....evmos.inflation.v1 import genesis_pb2 as evmos_dot_inflation_dot_v1_dot_genesis__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eevmos/inflation/v1/query.proto\x12\x12evmos.inflation.v1\x1a\x14gogoproto/gogo.proto\x1a\x1cgoogle/api/annotations.proto\x1a\x1ecosmos/base/v1beta1/coin.proto\x1a evmos/inflation/v1/genesis.proto"\x14\n\x12QueryPeriodRequest"%\n\x13QueryPeriodResponse\x12\x0e\n\x06period\x18\x01 \x01(\x04" \n\x1eQueryEpochMintProvisionRequest"\x92\x01\n\x1fQueryEpochMintProvisionResponse\x12o\n\x14epoch_mint_provision\x18\x01 \x01(\x0b2\x1c.cosmos.base.v1beta1.DecCoinB3\xc8\xde\x1f\x00\xaa\xdf\x1f+github.com/cosmos/cosmos-sdk/types.DecCoins"\x1b\n\x19QuerySkippedEpochsRequest"4\n\x1aQuerySkippedEpochsResponse\x12\x16\n\x0eskipped_epochs\x18\x01 \x01(\x04"\x1f\n\x1dQueryCirculatingSupplyRequest"\x8f\x01\n\x1eQueryCirculatingSupplyResponse\x12m\n\x12circulating_supply\x18\x01 \x01(\x0b2\x1c.cosmos.base.v1beta1.DecCoinB3\xc8\xde\x1f\x00\xaa\xdf\x1f+github.com/cosmos/cosmos-sdk/types.DecCoins"\x1b\n\x19QueryInflationRateRequest"d\n\x1aQueryInflationRateResponse\x12F\n\x0einflation_rate\x18\x01 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00"\x14\n\x12QueryParamsRequest"G\n\x13QueryParamsResponse\x120\n\x06params\x18\x01 \x01(\x0b2\x1a.evmos.inflation.v1.ParamsB\x04\xc8\xde\x1f\x002\x9e\x07\n\x05Query\x12}\n\x06Period\x12&.evmos.inflation.v1.QueryPeriodRequest\x1a\'.evmos.inflation.v1.QueryPeriodResponse""\x82\xd3\xe4\x93\x02\x1c\x12\x1a/evmos/inflation/v1/period\x12\xaf\x01\n\x12EpochMintProvision\x122.evmos.inflation.v1.QueryEpochMintProvisionRequest\x1a3.evmos.inflation.v1.QueryEpochMintProvisionResponse"0\x82\xd3\xe4\x93\x02*\x12(/evmos/inflation/v1/epoch_mint_provision\x12\x9a\x01\n\rSkippedEpochs\x12-.evmos.inflation.v1.QuerySkippedEpochsRequest\x1a..evmos.inflation.v1.QuerySkippedEpochsResponse"*\x82\xd3\xe4\x93\x02$\x12"/evmos/inflation/v1/skipped_epochs\x12\xaa\x01\n\x11CirculatingSupply\x121.evmos.inflation.v1.QueryCirculatingSupplyRequest\x1a2.evmos.inflation.v1.QueryCirculatingSupplyResponse".\x82\xd3\xe4\x93\x02(\x12&/evmos/inflation/v1/circulating_supply\x12\x9a\x01\n\rInflationRate\x12-.evmos.inflation.v1.QueryInflationRateRequest\x1a..evmos.inflation.v1.QueryInflationRateResponse"*\x82\xd3\xe4\x93\x02$\x12"/evmos/inflation/v1/inflation_rate\x12}\n\x06Params\x12&.evmos.inflation.v1.QueryParamsRequest\x1a\'.evmos.inflation.v1.QueryParamsResponse""\x82\xd3\xe4\x93\x02\x1c\x12\x1a/evmos/inflation/v1/paramsB-Z+github.com/evmos/evmos/v7/x/inflation/typesb\x06proto3')
_QUERYPERIODREQUEST = DESCRIPTOR.message_types_by_name['QueryPeriodRequest']
_QUERYPERIODRESPONSE = DESCRIPTOR.message_types_by_name['QueryPeriodResponse']
_QUERYEPOCHMINTPROVISIONREQUEST = DESCRIPTOR.message_types_by_name['QueryEpochMintProvisionRequest']
_QUERYEPOCHMINTPROVISIONRESPONSE = DESCRIPTOR.message_types_by_name['QueryEpochMintProvisionResponse']
_QUERYSKIPPEDEPOCHSREQUEST = DESCRIPTOR.message_types_by_name['QuerySkippedEpochsRequest']
_QUERYSKIPPEDEPOCHSRESPONSE = DESCRIPTOR.message_types_by_name['QuerySkippedEpochsResponse']
_QUERYCIRCULATINGSUPPLYREQUEST = DESCRIPTOR.message_types_by_name['QueryCirculatingSupplyRequest']
_QUERYCIRCULATINGSUPPLYRESPONSE = DESCRIPTOR.message_types_by_name['QueryCirculatingSupplyResponse']
_QUERYINFLATIONRATEREQUEST = DESCRIPTOR.message_types_by_name['QueryInflationRateRequest']
_QUERYINFLATIONRATERESPONSE = DESCRIPTOR.message_types_by_name['QueryInflationRateResponse']
_QUERYPARAMSREQUEST = DESCRIPTOR.message_types_by_name['QueryParamsRequest']
_QUERYPARAMSRESPONSE = DESCRIPTOR.message_types_by_name['QueryParamsResponse']
QueryPeriodRequest = _reflection.GeneratedProtocolMessageType('QueryPeriodRequest', (_message.Message,), {'DESCRIPTOR': _QUERYPERIODREQUEST, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryPeriodRequest)
QueryPeriodResponse = _reflection.GeneratedProtocolMessageType('QueryPeriodResponse', (_message.Message,), {'DESCRIPTOR': _QUERYPERIODRESPONSE, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryPeriodResponse)
QueryEpochMintProvisionRequest = _reflection.GeneratedProtocolMessageType('QueryEpochMintProvisionRequest', (_message.Message,), {'DESCRIPTOR': _QUERYEPOCHMINTPROVISIONREQUEST, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryEpochMintProvisionRequest)
QueryEpochMintProvisionResponse = _reflection.GeneratedProtocolMessageType('QueryEpochMintProvisionResponse', (_message.Message,), {'DESCRIPTOR': _QUERYEPOCHMINTPROVISIONRESPONSE, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryEpochMintProvisionResponse)
QuerySkippedEpochsRequest = _reflection.GeneratedProtocolMessageType('QuerySkippedEpochsRequest', (_message.Message,), {'DESCRIPTOR': _QUERYSKIPPEDEPOCHSREQUEST, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QuerySkippedEpochsRequest)
QuerySkippedEpochsResponse = _reflection.GeneratedProtocolMessageType('QuerySkippedEpochsResponse', (_message.Message,), {'DESCRIPTOR': _QUERYSKIPPEDEPOCHSRESPONSE, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QuerySkippedEpochsResponse)
QueryCirculatingSupplyRequest = _reflection.GeneratedProtocolMessageType('QueryCirculatingSupplyRequest', (_message.Message,), {'DESCRIPTOR': _QUERYCIRCULATINGSUPPLYREQUEST, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryCirculatingSupplyRequest)
QueryCirculatingSupplyResponse = _reflection.GeneratedProtocolMessageType('QueryCirculatingSupplyResponse', (_message.Message,), {'DESCRIPTOR': _QUERYCIRCULATINGSUPPLYRESPONSE, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryCirculatingSupplyResponse)
QueryInflationRateRequest = _reflection.GeneratedProtocolMessageType('QueryInflationRateRequest', (_message.Message,), {'DESCRIPTOR': _QUERYINFLATIONRATEREQUEST, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryInflationRateRequest)
QueryInflationRateResponse = _reflection.GeneratedProtocolMessageType('QueryInflationRateResponse', (_message.Message,), {'DESCRIPTOR': _QUERYINFLATIONRATERESPONSE, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryInflationRateResponse)
QueryParamsRequest = _reflection.GeneratedProtocolMessageType('QueryParamsRequest', (_message.Message,), {'DESCRIPTOR': _QUERYPARAMSREQUEST, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryParamsRequest)
QueryParamsResponse = _reflection.GeneratedProtocolMessageType('QueryParamsResponse', (_message.Message,), {'DESCRIPTOR': _QUERYPARAMSRESPONSE, '__module__': 'evmos.inflation.v1.query_pb2'})
_sym_db.RegisterMessage(QueryParamsResponse)
_QUERY = DESCRIPTOR.services_by_name['Query']
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z+github.com/evmos/evmos/v7/x/inflation/types'
    _QUERYEPOCHMINTPROVISIONRESPONSE.fields_by_name['epoch_mint_provision']._options = None
    _QUERYEPOCHMINTPROVISIONRESPONSE.fields_by_name['epoch_mint_provision']._serialized_options = b'\xc8\xde\x1f\x00\xaa\xdf\x1f+github.com/cosmos/cosmos-sdk/types.DecCoins'
    _QUERYCIRCULATINGSUPPLYRESPONSE.fields_by_name['circulating_supply']._options = None
    _QUERYCIRCULATINGSUPPLYRESPONSE.fields_by_name['circulating_supply']._serialized_options = b'\xc8\xde\x1f\x00\xaa\xdf\x1f+github.com/cosmos/cosmos-sdk/types.DecCoins'
    _QUERYINFLATIONRATERESPONSE.fields_by_name['inflation_rate']._options = None
    _QUERYINFLATIONRATERESPONSE.fields_by_name['inflation_rate']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _QUERYPARAMSRESPONSE.fields_by_name['params']._options = None
    _QUERYPARAMSRESPONSE.fields_by_name['params']._serialized_options = b'\xc8\xde\x1f\x00'
    _QUERY.methods_by_name['Period']._options = None
    _QUERY.methods_by_name['Period']._serialized_options = b'\x82\xd3\xe4\x93\x02\x1c\x12\x1a/evmos/inflation/v1/period'
    _QUERY.methods_by_name['EpochMintProvision']._options = None
    _QUERY.methods_by_name['EpochMintProvision']._serialized_options = b'\x82\xd3\xe4\x93\x02*\x12(/evmos/inflation/v1/epoch_mint_provision'
    _QUERY.methods_by_name['SkippedEpochs']._options = None
    _QUERY.methods_by_name['SkippedEpochs']._serialized_options = b'\x82\xd3\xe4\x93\x02$\x12"/evmos/inflation/v1/skipped_epochs'
    _QUERY.methods_by_name['CirculatingSupply']._options = None
    _QUERY.methods_by_name['CirculatingSupply']._serialized_options = b'\x82\xd3\xe4\x93\x02(\x12&/evmos/inflation/v1/circulating_supply'
    _QUERY.methods_by_name['InflationRate']._options = None
    _QUERY.methods_by_name['InflationRate']._serialized_options = b'\x82\xd3\xe4\x93\x02$\x12"/evmos/inflation/v1/inflation_rate'
    _QUERY.methods_by_name['Params']._options = None
    _QUERY.methods_by_name['Params']._serialized_options = b'\x82\xd3\xe4\x93\x02\x1c\x12\x1a/evmos/inflation/v1/params'
    _QUERYPERIODREQUEST._serialized_start = 172
    _QUERYPERIODREQUEST._serialized_end = 192
    _QUERYPERIODRESPONSE._serialized_start = 194
    _QUERYPERIODRESPONSE._serialized_end = 231
    _QUERYEPOCHMINTPROVISIONREQUEST._serialized_start = 233
    _QUERYEPOCHMINTPROVISIONREQUEST._serialized_end = 265
    _QUERYEPOCHMINTPROVISIONRESPONSE._serialized_start = 268
    _QUERYEPOCHMINTPROVISIONRESPONSE._serialized_end = 414
    _QUERYSKIPPEDEPOCHSREQUEST._serialized_start = 416
    _QUERYSKIPPEDEPOCHSREQUEST._serialized_end = 443
    _QUERYSKIPPEDEPOCHSRESPONSE._serialized_start = 445
    _QUERYSKIPPEDEPOCHSRESPONSE._serialized_end = 497
    _QUERYCIRCULATINGSUPPLYREQUEST._serialized_start = 499
    _QUERYCIRCULATINGSUPPLYREQUEST._serialized_end = 530
    _QUERYCIRCULATINGSUPPLYRESPONSE._serialized_start = 533
    _QUERYCIRCULATINGSUPPLYRESPONSE._serialized_end = 676
    _QUERYINFLATIONRATEREQUEST._serialized_start = 678
    _QUERYINFLATIONRATEREQUEST._serialized_end = 705
    _QUERYINFLATIONRATERESPONSE._serialized_start = 707
    _QUERYINFLATIONRATERESPONSE._serialized_end = 807
    _QUERYPARAMSREQUEST._serialized_start = 809
    _QUERYPARAMSREQUEST._serialized_end = 829
    _QUERYPARAMSRESPONSE._serialized_start = 831
    _QUERYPARAMSRESPONSE._serialized_end = 902
    _QUERY._serialized_start = 905
    _QUERY._serialized_end = 1831

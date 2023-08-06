
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n"evmos/inflation/v1/inflation.proto\x12\x12evmos.inflation.v1\x1a\x14gogoproto/gogo.proto"\xf2\x01\n\x15InflationDistribution\x12G\n\x0fstaking_rewards\x18\x01 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\x12H\n\x10usage_incentives\x18\x02 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\x12F\n\x0ecommunity_pool\x18\x03 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00"\xd7\x02\n\x16ExponentialCalculation\x129\n\x01a\x18\x01 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\x129\n\x01r\x18\x02 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\x129\n\x01c\x18\x03 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\x12F\n\x0ebonding_target\x18\x04 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\x12D\n\x0cmax_variance\x18\x05 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00B-Z+github.com/evmos/evmos/v7/x/inflation/typesb\x06proto3')
_INFLATIONDISTRIBUTION = DESCRIPTOR.message_types_by_name['InflationDistribution']
_EXPONENTIALCALCULATION = DESCRIPTOR.message_types_by_name['ExponentialCalculation']
InflationDistribution = _reflection.GeneratedProtocolMessageType('InflationDistribution', (_message.Message,), {'DESCRIPTOR': _INFLATIONDISTRIBUTION, '__module__': 'evmos.inflation.v1.inflation_pb2'})
_sym_db.RegisterMessage(InflationDistribution)
ExponentialCalculation = _reflection.GeneratedProtocolMessageType('ExponentialCalculation', (_message.Message,), {'DESCRIPTOR': _EXPONENTIALCALCULATION, '__module__': 'evmos.inflation.v1.inflation_pb2'})
_sym_db.RegisterMessage(ExponentialCalculation)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z+github.com/evmos/evmos/v7/x/inflation/types'
    _INFLATIONDISTRIBUTION.fields_by_name['staking_rewards']._options = None
    _INFLATIONDISTRIBUTION.fields_by_name['staking_rewards']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _INFLATIONDISTRIBUTION.fields_by_name['usage_incentives']._options = None
    _INFLATIONDISTRIBUTION.fields_by_name['usage_incentives']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _INFLATIONDISTRIBUTION.fields_by_name['community_pool']._options = None
    _INFLATIONDISTRIBUTION.fields_by_name['community_pool']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _EXPONENTIALCALCULATION.fields_by_name['a']._options = None
    _EXPONENTIALCALCULATION.fields_by_name['a']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _EXPONENTIALCALCULATION.fields_by_name['r']._options = None
    _EXPONENTIALCALCULATION.fields_by_name['r']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _EXPONENTIALCALCULATION.fields_by_name['c']._options = None
    _EXPONENTIALCALCULATION.fields_by_name['c']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _EXPONENTIALCALCULATION.fields_by_name['bonding_target']._options = None
    _EXPONENTIALCALCULATION.fields_by_name['bonding_target']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _EXPONENTIALCALCULATION.fields_by_name['max_variance']._options = None
    _EXPONENTIALCALCULATION.fields_by_name['max_variance']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00'
    _INFLATIONDISTRIBUTION._serialized_start = 81
    _INFLATIONDISTRIBUTION._serialized_end = 323
    _EXPONENTIALCALCULATION._serialized_start = 326
    _EXPONENTIALCALCULATION._serialized_end = 669

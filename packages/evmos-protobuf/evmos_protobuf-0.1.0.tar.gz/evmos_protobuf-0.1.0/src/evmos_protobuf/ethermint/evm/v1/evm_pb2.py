
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aethermint/evm/v1/evm.proto\x12\x10ethermint.evm.v1\x1a\x14gogoproto/gogo.proto"\xb8\x02\n\x06Params\x12\'\n\tevm_denom\x18\x01 \x01(\tB\x14\xf2\xde\x1f\x10yaml:"evm_denom"\x12/\n\renable_create\x18\x02 \x01(\x08B\x18\xf2\xde\x1f\x14yaml:"enable_create"\x12+\n\x0benable_call\x18\x03 \x01(\x08B\x16\xf2\xde\x1f\x12yaml:"enable_call"\x126\n\nextra_eips\x18\x04 \x03(\x03B"\xe2\xde\x1f\tExtraEIPs\xf2\xde\x1f\x11yaml:"extra_eips"\x12P\n\x0cchain_config\x18\x05 \x01(\x0b2\x1d.ethermint.evm.v1.ChainConfigB\x1b\xf2\xde\x1f\x13yaml:"chain_config"\xc8\xde\x1f\x00\x12\x1d\n\x15allow_unprotected_txs\x18\x06 \x01(\x08"\xbc\x0c\n\x0bChainConfig\x12]\n\x0fhomestead_block\x18\x01 \x01(\tBD\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x16yaml:"homestead_block"\x12k\n\x0edao_fork_block\x18\x02 \x01(\tBS\xe2\xde\x1f\x0cDAOForkBlock\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x15yaml:"dao_fork_block"\x12G\n\x10dao_fork_support\x18\x03 \x01(\x08B-\xe2\xde\x1f\x0eDAOForkSupport\xf2\xde\x1f\x17yaml:"dao_fork_support"\x12f\n\x0ceip150_block\x18\x04 \x01(\tBP\xe2\xde\x1f\x0bEIP150Block\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"eip150_block"\x12=\n\x0beip150_hash\x18\x05 \x01(\tB(\xe2\xde\x1f\nEIP150Hash\xf2\xde\x1f\x16yaml:"byzantium_block"\x12f\n\x0ceip155_block\x18\x06 \x01(\tBP\xe2\xde\x1f\x0bEIP155Block\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"eip155_block"\x12f\n\x0ceip158_block\x18\x07 \x01(\tBP\xe2\xde\x1f\x0bEIP158Block\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"eip158_block"\x12]\n\x0fbyzantium_block\x18\x08 \x01(\tBD\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x16yaml:"byzantium_block"\x12g\n\x14constantinople_block\x18\t \x01(\tBI\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x1byaml:"constantinople_block"\x12_\n\x10petersburg_block\x18\n \x01(\tBE\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x17yaml:"petersburg_block"\x12[\n\x0eistanbul_block\x18\x0b \x01(\tBC\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x15yaml:"istanbul_block"\x12c\n\x12muir_glacier_block\x18\x0c \x01(\tBG\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x19yaml:"muir_glacier_block"\x12W\n\x0cberlin_block\x18\r \x01(\tBA\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"berlin_block"\x12W\n\x0clondon_block\x18\x11 \x01(\tBA\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"london_block"\x12e\n\x13arrow_glacier_block\x18\x12 \x01(\tBH\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x1ayaml:"arrow_glacier_block"\x12_\n\x10merge_fork_block\x18\x13 \x01(\tBE\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x17yaml:"merge_fork_block"J\x04\x08\x0e\x10\x0fJ\x04\x08\x0f\x10\x10J\x04\x08\x10\x10\x11R\ryolo_v3_blockR\x0bewasm_blockR\x0ecatalyst_block"#\n\x05State\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t"D\n\x0fTransactionLogs\x12\x0c\n\x04hash\x18\x01 \x01(\t\x12#\n\x04logs\x18\x02 \x03(\x0b2\x15.ethermint.evm.v1.Log"\xfa\x01\n\x03Log\x12\x0f\n\x07address\x18\x01 \x01(\t\x12\x0e\n\x06topics\x18\x02 \x03(\t\x12\x0c\n\x04data\x18\x03 \x01(\x0c\x12%\n\x0cblock_number\x18\x04 \x01(\x04B\x0f\xea\xde\x1f\x0bblockNumber\x12$\n\x07tx_hash\x18\x05 \x01(\tB\x13\xea\xde\x1f\x0ftransactionHash\x12&\n\x08tx_index\x18\x06 \x01(\x04B\x14\xea\xde\x1f\x10transactionIndex\x12!\n\nblock_hash\x18\x07 \x01(\tB\r\xea\xde\x1f\tblockHash\x12\x1b\n\x05index\x18\x08 \x01(\x04B\x0c\xea\xde\x1f\x08logIndex\x12\x0f\n\x07removed\x18\t \x01(\x08"\xd3\x01\n\x08TxResult\x125\n\x10contract_address\x18\x01 \x01(\tB\x1b\xf2\xde\x1f\x17yaml:"contract_address"\x12\r\n\x05bloom\x18\x02 \x01(\x0c\x12J\n\x07tx_logs\x18\x03 \x01(\x0b2!.ethermint.evm.v1.TransactionLogsB\x16\xf2\xde\x1f\x0eyaml:"tx_logs"\xc8\xde\x1f\x00\x12\x0b\n\x03ret\x18\x04 \x01(\x0c\x12\x10\n\x08reverted\x18\x05 \x01(\x08\x12\x10\n\x08gas_used\x18\x06 \x01(\x04:\x04\x88\xa0\x1f\x00"K\n\x0bAccessTuple\x12\x0f\n\x07address\x18\x01 \x01(\t\x12%\n\x0cstorage_keys\x18\x02 \x03(\tB\x0f\xea\xde\x1f\x0bstorageKeys:\x04\x88\xa0\x1f\x00"\xf0\x02\n\x0bTraceConfig\x12\x0e\n\x06tracer\x18\x01 \x01(\t\x12\x0f\n\x07timeout\x18\x02 \x01(\t\x12\x0e\n\x06reexec\x18\x03 \x01(\x04\x12\'\n\rdisable_stack\x18\x05 \x01(\x08B\x10\xea\xde\x1f\x0cdisableStack\x12+\n\x0fdisable_storage\x18\x06 \x01(\x08B\x12\xea\xde\x1f\x0edisableStorage\x12\r\n\x05debug\x18\x08 \x01(\x08\x12\r\n\x05limit\x18\t \x01(\x05\x120\n\toverrides\x18\n \x01(\x0b2\x1d.ethermint.evm.v1.ChainConfig\x12\'\n\renable_memory\x18\x0b \x01(\x08B\x10\xea\xde\x1f\x0cenableMemory\x120\n\x12enable_return_data\x18\x0c \x01(\x08B\x14\xea\xde\x1f\x10enableReturnDataJ\x04\x08\x04\x10\x05J\x04\x08\x07\x10\x08R\x0edisable_memoryR\x13disable_return_dataB(Z&github.com/evmos/ethermint/x/evm/typesb\x06proto3')
_PARAMS = DESCRIPTOR.message_types_by_name['Params']
_CHAINCONFIG = DESCRIPTOR.message_types_by_name['ChainConfig']
_STATE = DESCRIPTOR.message_types_by_name['State']
_TRANSACTIONLOGS = DESCRIPTOR.message_types_by_name['TransactionLogs']
_LOG = DESCRIPTOR.message_types_by_name['Log']
_TXRESULT = DESCRIPTOR.message_types_by_name['TxResult']
_ACCESSTUPLE = DESCRIPTOR.message_types_by_name['AccessTuple']
_TRACECONFIG = DESCRIPTOR.message_types_by_name['TraceConfig']
Params = _reflection.GeneratedProtocolMessageType('Params', (_message.Message,), {'DESCRIPTOR': _PARAMS, '__module__': 'ethermint.evm.v1.evm_pb2'})
_sym_db.RegisterMessage(Params)
ChainConfig = _reflection.GeneratedProtocolMessageType('ChainConfig', (_message.Message,), {'DESCRIPTOR': _CHAINCONFIG, '__module__': 'ethermint.evm.v1.evm_pb2'})
_sym_db.RegisterMessage(ChainConfig)
State = _reflection.GeneratedProtocolMessageType('State', (_message.Message,), {'DESCRIPTOR': _STATE, '__module__': 'ethermint.evm.v1.evm_pb2'})
_sym_db.RegisterMessage(State)
TransactionLogs = _reflection.GeneratedProtocolMessageType('TransactionLogs', (_message.Message,), {'DESCRIPTOR': _TRANSACTIONLOGS, '__module__': 'ethermint.evm.v1.evm_pb2'})
_sym_db.RegisterMessage(TransactionLogs)
Log = _reflection.GeneratedProtocolMessageType('Log', (_message.Message,), {'DESCRIPTOR': _LOG, '__module__': 'ethermint.evm.v1.evm_pb2'})
_sym_db.RegisterMessage(Log)
TxResult = _reflection.GeneratedProtocolMessageType('TxResult', (_message.Message,), {'DESCRIPTOR': _TXRESULT, '__module__': 'ethermint.evm.v1.evm_pb2'})
_sym_db.RegisterMessage(TxResult)
AccessTuple = _reflection.GeneratedProtocolMessageType('AccessTuple', (_message.Message,), {'DESCRIPTOR': _ACCESSTUPLE, '__module__': 'ethermint.evm.v1.evm_pb2'})
_sym_db.RegisterMessage(AccessTuple)
TraceConfig = _reflection.GeneratedProtocolMessageType('TraceConfig', (_message.Message,), {'DESCRIPTOR': _TRACECONFIG, '__module__': 'ethermint.evm.v1.evm_pb2'})
_sym_db.RegisterMessage(TraceConfig)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z&github.com/evmos/ethermint/x/evm/types'
    _PARAMS.fields_by_name['evm_denom']._options = None
    _PARAMS.fields_by_name['evm_denom']._serialized_options = b'\xf2\xde\x1f\x10yaml:"evm_denom"'
    _PARAMS.fields_by_name['enable_create']._options = None
    _PARAMS.fields_by_name['enable_create']._serialized_options = b'\xf2\xde\x1f\x14yaml:"enable_create"'
    _PARAMS.fields_by_name['enable_call']._options = None
    _PARAMS.fields_by_name['enable_call']._serialized_options = b'\xf2\xde\x1f\x12yaml:"enable_call"'
    _PARAMS.fields_by_name['extra_eips']._options = None
    _PARAMS.fields_by_name['extra_eips']._serialized_options = b'\xe2\xde\x1f\tExtraEIPs\xf2\xde\x1f\x11yaml:"extra_eips"'
    _PARAMS.fields_by_name['chain_config']._options = None
    _PARAMS.fields_by_name['chain_config']._serialized_options = b'\xf2\xde\x1f\x13yaml:"chain_config"\xc8\xde\x1f\x00'
    _CHAINCONFIG.fields_by_name['homestead_block']._options = None
    _CHAINCONFIG.fields_by_name['homestead_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x16yaml:"homestead_block"'
    _CHAINCONFIG.fields_by_name['dao_fork_block']._options = None
    _CHAINCONFIG.fields_by_name['dao_fork_block']._serialized_options = b'\xe2\xde\x1f\x0cDAOForkBlock\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x15yaml:"dao_fork_block"'
    _CHAINCONFIG.fields_by_name['dao_fork_support']._options = None
    _CHAINCONFIG.fields_by_name['dao_fork_support']._serialized_options = b'\xe2\xde\x1f\x0eDAOForkSupport\xf2\xde\x1f\x17yaml:"dao_fork_support"'
    _CHAINCONFIG.fields_by_name['eip150_block']._options = None
    _CHAINCONFIG.fields_by_name['eip150_block']._serialized_options = b'\xe2\xde\x1f\x0bEIP150Block\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"eip150_block"'
    _CHAINCONFIG.fields_by_name['eip150_hash']._options = None
    _CHAINCONFIG.fields_by_name['eip150_hash']._serialized_options = b'\xe2\xde\x1f\nEIP150Hash\xf2\xde\x1f\x16yaml:"byzantium_block"'
    _CHAINCONFIG.fields_by_name['eip155_block']._options = None
    _CHAINCONFIG.fields_by_name['eip155_block']._serialized_options = b'\xe2\xde\x1f\x0bEIP155Block\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"eip155_block"'
    _CHAINCONFIG.fields_by_name['eip158_block']._options = None
    _CHAINCONFIG.fields_by_name['eip158_block']._serialized_options = b'\xe2\xde\x1f\x0bEIP158Block\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"eip158_block"'
    _CHAINCONFIG.fields_by_name['byzantium_block']._options = None
    _CHAINCONFIG.fields_by_name['byzantium_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x16yaml:"byzantium_block"'
    _CHAINCONFIG.fields_by_name['constantinople_block']._options = None
    _CHAINCONFIG.fields_by_name['constantinople_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x1byaml:"constantinople_block"'
    _CHAINCONFIG.fields_by_name['petersburg_block']._options = None
    _CHAINCONFIG.fields_by_name['petersburg_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x17yaml:"petersburg_block"'
    _CHAINCONFIG.fields_by_name['istanbul_block']._options = None
    _CHAINCONFIG.fields_by_name['istanbul_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x15yaml:"istanbul_block"'
    _CHAINCONFIG.fields_by_name['muir_glacier_block']._options = None
    _CHAINCONFIG.fields_by_name['muir_glacier_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x19yaml:"muir_glacier_block"'
    _CHAINCONFIG.fields_by_name['berlin_block']._options = None
    _CHAINCONFIG.fields_by_name['berlin_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"berlin_block"'
    _CHAINCONFIG.fields_by_name['london_block']._options = None
    _CHAINCONFIG.fields_by_name['london_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x13yaml:"london_block"'
    _CHAINCONFIG.fields_by_name['arrow_glacier_block']._options = None
    _CHAINCONFIG.fields_by_name['arrow_glacier_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x1ayaml:"arrow_glacier_block"'
    _CHAINCONFIG.fields_by_name['merge_fork_block']._options = None
    _CHAINCONFIG.fields_by_name['merge_fork_block']._serialized_options = b'\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xf2\xde\x1f\x17yaml:"merge_fork_block"'
    _LOG.fields_by_name['block_number']._options = None
    _LOG.fields_by_name['block_number']._serialized_options = b'\xea\xde\x1f\x0bblockNumber'
    _LOG.fields_by_name['tx_hash']._options = None
    _LOG.fields_by_name['tx_hash']._serialized_options = b'\xea\xde\x1f\x0ftransactionHash'
    _LOG.fields_by_name['tx_index']._options = None
    _LOG.fields_by_name['tx_index']._serialized_options = b'\xea\xde\x1f\x10transactionIndex'
    _LOG.fields_by_name['block_hash']._options = None
    _LOG.fields_by_name['block_hash']._serialized_options = b'\xea\xde\x1f\tblockHash'
    _LOG.fields_by_name['index']._options = None
    _LOG.fields_by_name['index']._serialized_options = b'\xea\xde\x1f\x08logIndex'
    _TXRESULT.fields_by_name['contract_address']._options = None
    _TXRESULT.fields_by_name['contract_address']._serialized_options = b'\xf2\xde\x1f\x17yaml:"contract_address"'
    _TXRESULT.fields_by_name['tx_logs']._options = None
    _TXRESULT.fields_by_name['tx_logs']._serialized_options = b'\xf2\xde\x1f\x0eyaml:"tx_logs"\xc8\xde\x1f\x00'
    _TXRESULT._options = None
    _TXRESULT._serialized_options = b'\x88\xa0\x1f\x00'
    _ACCESSTUPLE.fields_by_name['storage_keys']._options = None
    _ACCESSTUPLE.fields_by_name['storage_keys']._serialized_options = b'\xea\xde\x1f\x0bstorageKeys'
    _ACCESSTUPLE._options = None
    _ACCESSTUPLE._serialized_options = b'\x88\xa0\x1f\x00'
    _TRACECONFIG.fields_by_name['disable_stack']._options = None
    _TRACECONFIG.fields_by_name['disable_stack']._serialized_options = b'\xea\xde\x1f\x0cdisableStack'
    _TRACECONFIG.fields_by_name['disable_storage']._options = None
    _TRACECONFIG.fields_by_name['disable_storage']._serialized_options = b'\xea\xde\x1f\x0edisableStorage'
    _TRACECONFIG.fields_by_name['enable_memory']._options = None
    _TRACECONFIG.fields_by_name['enable_memory']._serialized_options = b'\xea\xde\x1f\x0cenableMemory'
    _TRACECONFIG.fields_by_name['enable_return_data']._options = None
    _TRACECONFIG.fields_by_name['enable_return_data']._serialized_options = b'\xea\xde\x1f\x10enableReturnData'
    _PARAMS._serialized_start = 71
    _PARAMS._serialized_end = 383
    _CHAINCONFIG._serialized_start = 386
    _CHAINCONFIG._serialized_end = 1982
    _STATE._serialized_start = 1984
    _STATE._serialized_end = 2019
    _TRANSACTIONLOGS._serialized_start = 2021
    _TRANSACTIONLOGS._serialized_end = 2089
    _LOG._serialized_start = 2092
    _LOG._serialized_end = 2342
    _TXRESULT._serialized_start = 2345
    _TXRESULT._serialized_end = 2556
    _ACCESSTUPLE._serialized_start = 2558
    _ACCESSTUPLE._serialized_end = 2633
    _TRACECONFIG._serialized_start = 2636
    _TRACECONFIG._serialized_end = 3004

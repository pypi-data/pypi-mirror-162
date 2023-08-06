import copy
import json
from typing import (
    Optional,
    Any,
    cast,
    TYPE_CHECKING,
)

import rlp
from hexbytes import HexBytes

from platon._utils.error_code import ERROR_CODE
from platon.module import apply_result_formatters

from platon.exceptions import (
    ContractLogicError,
)
from platon_typing import (
    HexStr,
    Bech32Address,
)
from platon_utils import (
    to_bech32_address, remove_0x_prefix,
)
from platon._utils.empty import (
    empty,
)
from platon._utils.rpc_abi import (
    apply_abi_formatters_to_dict,
)
from platon._utils.transactions import (
    fill_transaction_defaults,
)
from platon._utils.contract_formatter import (
    INNER_CONTRACT_PARAM_ABIS,
    DEFAULT_PARAM_NORMALIZERS,
    DEFAULT_PARAM_ABIS,
    INNER_CONTRACT_RESULT_FORMATTERS,
)
from platon.types import (
    TxParams,
    BlockIdentifier,
    CallOverrideParams,
    FunctionIdentifier, TxReceipt, EventData, LogReceipt, CodeData,
)

if TYPE_CHECKING:
    from platon import Web3


class InnerContract:
    _HEX_ADDRESS = None
    _address = None
    _function = None
    _event = None

    # If you want to get the result of the transaction, please set it to True,
    # if you only want to get the transaction hash, please set it to False
    # is_analyze = False

    def __init__(self, web3: "Web3"):
        self.web3: Web3 = web3

    @property
    def address(self):
        if not self._address:
            self._address = to_bech32_address(self._HEX_ADDRESS, self.web3.hrp)
        return self._address

    @property
    def function(self):
        if not self._function:
            self._function = InnerContractFunction(self.web3, self.address)
        return self._function

    @property
    def event(self):
        if not self._event:
            self._event = InnerContractEvent()
        return self._event

    def function_processor(self, func_type: FunctionIdentifier, kwargs: dict, is_call: bool = False) -> callable:
        self.kwargs_process(kwargs)
        if is_call:
            return self.function(func_type, kwargs).call()
        return self.function(func_type, kwargs)

    @staticmethod
    def kwargs_process(kwargs: dict):
        kwargs.pop("self")
        for key, value in kwargs.items():
            if type(value) is dict:
                raise ValueError("Invalid argument: {}, the value cannot be a dict".format(key))


class InnerContractFunction:
    func_id: FunctionIdentifier = None
    kwargs: dict = None

    def __init__(self, web3: "Web3", address: Bech32Address):
        self.web3: Web3 = web3
        self.address: Bech32Address = address

    def __call__(self, func_type: FunctionIdentifier, kwargs: dict) -> 'InnerContractFunction':
        clone = copy.copy(self)
        clone.func_id = func_type
        if kwargs is None:
            clone.kwargs = {}
        else:
            clone.kwargs = copy.copy(kwargs)

        return clone

    def call(self,
             transaction: Optional[TxParams] = None,
             block_identifier: BlockIdentifier = 'latest',
             state_override: Optional[CallOverrideParams] = None,
             ) -> Any:

        if transaction is None:
            call_transaction: TxParams = {}
        else:
            call_transaction = cast(TxParams, dict(**transaction))

        if 'data' in call_transaction:
            raise ValueError("Cannot set data in call transaction")

        if 'to' in call_transaction:
            raise ValueError("Cannot set to address in contract call transaction")

        if self.address:
            call_transaction.setdefault('to', self.address)

        if self.web3.platon.default_account is not empty:
            # type ignored b/c check prevents an empty default_account
            call_transaction.setdefault('from', self.web3.platon.default_account)  # type: ignore

        if 'to' not in call_transaction:
            raise ValueError(
                "Please ensure that this inner contract instance has an address."
            )

        call_transaction['data'] = self._encode_transaction_data()

        return_data = self.web3.platon.call(call_transaction,
                                            block_identifier=block_identifier,
                                            state_override=state_override,
                                            )

        return self._formatter_result(self.func_id, return_data)

    def transact(self):
        # todo: wait coding
        pass

    def estimate_gas(self,
                     transaction: Optional[TxParams] = None,
                     block_identifier: Optional[BlockIdentifier] = None
                     ) -> int:
        if transaction is None:
            estimate_transaction: TxParams = {}
        else:
            estimate_transaction = cast(TxParams, dict(**transaction))

        if 'data' in estimate_transaction:
            raise ValueError("Cannot set data in build transaction")

        if 'to' in estimate_transaction:
            raise ValueError("Cannot set to address in contract call build transaction")

        if self.address:
            estimate_transaction.setdefault('to', self.address)

        if 'to' not in estimate_transaction:
            raise ValueError(
                "Please ensure that this inner contract instance has an address."
            )

        estimate_transaction['data'] = self._encode_transaction_data()

        return self.web3.platon.estimate_gas(estimate_transaction, block_identifier)

    def build_transaction(self, transaction: Optional[TxParams] = None) -> TxParams:
        """
        Build the transaction dictionary without sending
        """
        if transaction is None:
            built_transaction: TxParams = {}
        else:
            built_transaction = cast(TxParams, dict(**transaction))

        if 'data' in built_transaction:
            raise ValueError("Cannot set data in build transaction")

        if 'to' in built_transaction:
            raise ValueError("Cannot set to address in contract call build transaction")

        if self.address:
            built_transaction.setdefault('to', self.address)

        if 'to' not in built_transaction:
            raise ValueError(
                "Please ensure that this inner contract instance has an address."
            )

        built_transaction['data'] = self._encode_transaction_data()

        built_transaction = fill_transaction_defaults(self.web3, built_transaction)

        return built_transaction

    def _encode_transaction_data(self) -> HexStr:
        encoded_args = [rlp.encode(self.func_id)]

        self.kwargs = self._formatter_kwargs(self.func_id, kwargs=self.kwargs)
        if self.kwargs:
            # encodes parameters sequentially
            for key, value in self.kwargs.items():
                if value is None:
                    encoded_args.append(b'')
                else:
                    encoded_args.append(rlp.encode(value))

        return rlp.encode(encoded_args)

    @staticmethod
    def _formatter_kwargs(func_id: FunctionIdentifier, kwargs: dict):
        """
        Format parameters so that it can be used correctly during RPC encoding
        """
        kwargs = apply_abi_formatters_to_dict(DEFAULT_PARAM_NORMALIZERS,
                                              DEFAULT_PARAM_ABIS,
                                              kwargs)
        function_abis = INNER_CONTRACT_PARAM_ABIS.get(func_id)
        if function_abis:
            return apply_abi_formatters_to_dict(DEFAULT_PARAM_NORMALIZERS, function_abis, kwargs)
        return kwargs

    @staticmethod
    def _formatter_result(func_id: FunctionIdentifier, result: Any):
        """
        Format result to make its easier to use
        """
        if type(result) in [bytes, HexBytes]:
            result = json.loads(HexBytes(result).decode('utf-8'))

        if 'Code' not in result.keys() or 'Ret' not in result.keys():
            return result

        rets = result.get('Ret')

        if result.get('Code') != 0:
            # todo: Wait platon resolve the return value issue
            # raise ContractLogicError(rets)
            return rets

        # when rest is empty value, as <''> \ <[]> ...
        if not rets:
            return rets

        function_formatter = INNER_CONTRACT_RESULT_FORMATTERS.get(func_id)

        if function_formatter:
            return apply_result_formatters(function_formatter, rets)

        return rets


class InnerContractEvent:

    @classmethod
    def get_event(cls, transaction_receipt: TxReceipt) -> EventData:
        logs = transaction_receipt['logs']
        code_data = cls._get_code(logs[0])
        # todo: add code data to event data
        return code_data

    @classmethod
    def _get_code(cls, log: LogReceipt) -> CodeData:
        encoded_data = log.get('data')
        if type(encoded_data) is str:
            encoded_data = remove_0x_prefix(encoded_data)
        rlp_data_list = rlp.decode(bytes.fromhex(encoded_data))
        data = bytes.decode(rlp_data_list[0])
        try:
            # compatible historical versions
            return json.loads(data)
        finally:
            code = int(data)
            error_msg = ERROR_CODE.get(int(code), 'Unknown error code')
            return {'code': code, 'message': error_msg}


def bubble_dict(target: dict, *keys: Any):
    """
    rebuild dict and bubble the keys to top
    """
    copy_dict = copy.copy(target)
    new_dict = dict()
    for key in keys:
        value = copy_dict.pop(key)
        new_dict.update({key: value})
    new_dict.update(copy_dict)
    return new_dict

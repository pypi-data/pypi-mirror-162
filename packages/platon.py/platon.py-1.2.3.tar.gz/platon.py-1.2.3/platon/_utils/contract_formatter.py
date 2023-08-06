from platon_utils.curried import apply_formatters_to_dict, apply_formatter_if

from platon._utils.method_formatters import to_integer_if_hex, apply_list_to_array_formatter, is_not_null

from platon.types import (
    InnerFn,
)
from platon._utils.normalizers import (
    abi_bytes_to_bytes,
    abi_address_to_bytes,
)

DEFAULT_PARAM_NORMALIZERS = [
    abi_bytes_to_bytes,
    abi_address_to_bytes,
]

DEFAULT_PARAM_ABIS = {
    'address': 'address',
    'node_id': 'bytes',
    'proposal_id': 'bytes',
}

CREATE_STAKING_PARAM_ABIS = {
    'benefit_address': 'address',
    'node_id': 'bytes',
    'version_sign': 'bytes',
    'bls_pubkey': 'bytes',
    'bls_proof': 'bytes',
}

EDIT_CANDIDATE_PARAM_ABIS = {
    'benefit_address': 'address',
    'node_id': 'bytes',
}

GET_DELEGATE_LIST_PARAM_ABIS = {
    'delegate_address': 'address',
}

GET_DELEGATE_INFO_PARAM_ABIS = {
    'delegate_address': 'address',
}

VOTE_PARAM_ABIS = {
    'version_sign': 'bytes',
}

DECLARE_VERSION_PARAM_ABIS = {
    'version_sign': 'bytes',
}

CREATE_RESTRICTING_PARAM_ABIS = {
    'release_address': 'address',
}

GET_RESTRICTING_INFO_PARAM_ABIS = {
    'release_address': 'address',
}

INNER_CONTRACT_PARAM_ABIS = {
    # restricting
    InnerFn.restricting_createRestricting: CREATE_RESTRICTING_PARAM_ABIS,
    InnerFn.restricting_getRestrictingInfo: GET_RESTRICTING_INFO_PARAM_ABIS,
    # staking
    InnerFn.staking_createStaking: CREATE_STAKING_PARAM_ABIS,
    InnerFn.staking_editStaking: EDIT_CANDIDATE_PARAM_ABIS,
    InnerFn.delegate_getDelegateList: GET_DELEGATE_LIST_PARAM_ABIS,
    InnerFn.delegate_getDelegateInfo: GET_DELEGATE_INFO_PARAM_ABIS,
    # govern
    InnerFn.govern_vote: VOTE_PARAM_ABIS,
    InnerFn.govern_declareVersion: DECLARE_VERSION_PARAM_ABIS,
}

RESTRICTING_PLAN_FORMATTER = {
    'amount': to_integer_if_hex,
}

restricting_plan_formatter = apply_formatters_to_dict(RESTRICTING_PLAN_FORMATTER)

RESTRICTING_INFO_FORMATTER = {
    'balance': to_integer_if_hex,
    'Pledge': to_integer_if_hex,
    'debt': to_integer_if_hex,
    'plans': apply_formatter_if(is_not_null, apply_list_to_array_formatter(restricting_plan_formatter))
}

restricting_info_formatter = apply_formatters_to_dict(RESTRICTING_INFO_FORMATTER)

CANDIDATE_INFO_FORMATTER = {
    'Shares': to_integer_if_hex,
    'Released': to_integer_if_hex,
    'ReleasedHes': to_integer_if_hex,
    'RestrictingPlan': to_integer_if_hex,
    'RestrictingPlanHes': to_integer_if_hex,
    'DelegateTotal': to_integer_if_hex,
    'DelegateTotalHes': to_integer_if_hex,
    'DelegateRewardTotal': to_integer_if_hex,
}

candidate_info_formatter = apply_formatters_to_dict(CANDIDATE_INFO_FORMATTER)

VERIFIER_INFO_FORMATTER = {
    'Shares': to_integer_if_hex,
    'DelegateTotal': to_integer_if_hex,
    'DelegateRewardTotal': to_integer_if_hex,
}

verifier_info_formatter = apply_formatters_to_dict(VERIFIER_INFO_FORMATTER)

VALIDATOR_INFO_FORMATTER = {
    'Shares': to_integer_if_hex,
    'DelegateTotal': to_integer_if_hex,
    'DelegateRewardTotal': to_integer_if_hex,
}

validator_info_formatter = apply_formatters_to_dict(VALIDATOR_INFO_FORMATTER)

DELEGATE_INFO_FORMATTER = {
    'Released': to_integer_if_hex,
    'ReleasedHes': to_integer_if_hex,
    'RestrictingPlan': to_integer_if_hex,
    'RestrictingPlanHes': to_integer_if_hex,
    'CumulativeIncome': to_integer_if_hex,
}

delegate_info_formatter = apply_formatters_to_dict(DELEGATE_INFO_FORMATTER)

DELEGATE_REWARD_FORMATTER = {
    'reward': to_integer_if_hex,
}

delegate_reward_formatter = apply_formatters_to_dict(DELEGATE_REWARD_FORMATTER)

INNER_CONTRACT_RESULT_FORMATTERS = {
    InnerFn.restricting_getRestrictingInfo: restricting_info_formatter,
    InnerFn.staking_getCandidateList: apply_list_to_array_formatter(candidate_info_formatter),
    InnerFn.staking_getVerifierList: apply_list_to_array_formatter(verifier_info_formatter),
    InnerFn.staking_getValidatorList: apply_list_to_array_formatter(validator_info_formatter),
    InnerFn.staking_getCandidateInfo: candidate_info_formatter,
    InnerFn.staking_getBlockReward: to_integer_if_hex,
    InnerFn.staking_getStakingReward: to_integer_if_hex,
    InnerFn.delegate_getDelegateInfo: delegate_info_formatter,
    InnerFn.delegate_getDelegateReward: apply_list_to_array_formatter(delegate_reward_formatter),
}

network_message_types = {
    'transaction': 1,
    'transaction-request': 2,
    'join-request': 3,
    'blockchain': 4,
    'exit-request': 5,
    'create-block': 6,
    'attestation': 7,
}

consensus_message_types = {
    'start-loop': 1,
    'forger-id': 2,
    'create-block': 3,
    'check-block': 4,
}

parent_message_types = {
    'genesis-timestamp': 1,
    'end-cycle': 2,
    'stop': 3
}

# epoch duration in seconds
consensus_epoch_duration = 12

# don't add events from last ingore_time_delta seconds to blockchain to make sure all nodes received the information
ignore_time_delta = 5

generator_wallet_amount = 1_000_000_000
minimum_validator_balance = 32

penalty_percentage = 0.15
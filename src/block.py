import random
from typing import Any, Iterable, Mapping
from datetime import datetime
from transaction import Transaction, transaction_from_dict
from Crypto.Hash import SHA256
import json

# Every time a block forger sends a block that less than x% from the stake agree with it gets a penalty
class Penalty:
    def __init__(
            self,
            timestamp: float,
            validator_id: str):
        self._timestamp = timestamp
        self._validator_id = validator_id

    def to_dict(self):
        return {
            "timestamp": self._timestamp,
            "validator-id": self._validator_id
        }
    
    def get_timestamp(self):
        return self._timestamp
    
    def get_validator_id(self):
        return self._validator_id
    
    def __eq__(self, other: 'Penalty') -> bool:
        return self.__dict__ == other.__dict__


class Block:
    def __init__(
            self,
            forger_id: str,
            previous_hash: str,
            timestamp: float,
            transactions: Iterable[Transaction],
            penalties: Iterable[Penalty],
            join_requests: Iterable[Transaction]):
        self._forger_id = forger_id
        random.seed()
        self._next_seed = random.randint(1, pow(2, 32))
        self._previous_hash = previous_hash
        self._timestamp = timestamp
        # data ordered by timestamp
        self._transactions = transactions
        self._penalties = penalties
        self._join_requests = join_requests

    def to_dict(self):
        return {
            "timestamp": self._timestamp,
            "previous-hash": self._previous_hash,
            "forger-id": self._forger_id,
            "transactions": [
                transaction.to_dict() for transaction in self._transactions
            ],
            "penalties": [
                penalty.to_dict() for penalty in self._penalties
            ],
            "join-requests": [
                join_request.to_dict() for join_request in self._join_requests
            ]
        }

    def to_json(self) -> str:
        block_data = self.to_dict()
        return json.dumps(block_data)

    def to_bytes(self) -> bytes:
        return self.to_json().encode("utf-8")

    def calculate_hash(self) -> str:
        block_data = self.to_bytes()
        block_hash = SHA256.new(block_data)
        return block_hash.hexdigest()


def penalty_from_dict(penalty_data: Mapping[str, Any]) -> Block:
    return Penalty(
        timestamp=penalty_data['timestamp'],
        validator_id=penalty_data['validator-id']
    )


def block_from_dict(block_data: Mapping[str, Any]) -> Block:
    transactions = [
        transaction_from_dict(transaction_data) for transaction_data in block_data['transactions']
    ]
    join_requests = [
        transaction_from_dict(join_request_data) for join_request_data in block_data['join-requests']
    ]

    penalties = [
        penalty_from_dict(penalty_data) for penalty_data in block_data['penalties']
    ]

    return Block(
        forger_id=block_data['forger-id'],
        previous_hash=block_data['previous-hash'],
        timestamp=block_data['timestamp'],
        transactions=transactions,
        penalties=penalties,
        join_requests=join_requests
    )
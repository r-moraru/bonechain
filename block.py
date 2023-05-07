from typing import Iterable
from datetime import datetime
from transaction import Transaction
from Crypto.Hash import SHA256
import json

class Block:
    def __init__(self, previous_hash: str, transactions: Iterable[Transaction]):
        self._previous_hash = previous_hash
        self._transactions = transactions
        self._timestamp = datetime.now().timestamp()

    def to_json(self) -> str:
        block_data = {
            "timestamp": self._timestamp,
            "previous_hash": self._previous_hash,
            "transactions": [
                transaction.to_json() for transaction in self._transactions
            ]
        }

        return json.dumps(block_data)
    
    def to_bytes(self) -> bytes:
        return self.to_json().encode("utf-8")

    def calculate_hash(self) -> str:
        block_data = self.to_bytes()
        block_hash = SHA256.new(block_data)
        return block_hash.hexdigest()

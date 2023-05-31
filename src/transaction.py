from datetime import datetime
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from typing import Optional, Mapping, Any
import json


class Transaction:
    def __init__(
            self,
            sender_address: str,
            recipient_address: str,
            amount: int,
            signature: Optional[str] = None,
            timestamp: Optional[float] = None):
        self._sender_address = sender_address
        self._timestamp = timestamp or datetime.now().timestamp()
        self._recipient_address = recipient_address
        self._amount = amount
        self._signature = signature

    def get_sender_address(self) -> str:
        return self._sender_address
    
    def get_timestamp(self) -> float:
        return self._timestamp

    def get_recipient_address(self) -> str:
        return self._recipient_address
    
    def get_amount(self) -> int:
        return self._amount
    
    def get_signature(self) -> str:
        return self._signature

    def add_signature(self, signature: str):
        self._signature = signature

    def to_dict(self, exclude_signature: Optional[bool] = False):
        transaction_data = {
            "timestamp": self._timestamp,
            "sender": self._sender_address,
            "recipient": self._recipient_address,
            "amount": self._amount
        }
        if self._signature and not exclude_signature:
            transaction_data["signature"] = self._signature

        return transaction_data

    def to_json(self, exclude_signature: Optional[bool] = False) -> str:
        transaction_data = self.to_dict(exclude_signature=exclude_signature)
        return json.dumps(transaction_data)
    
    def to_bytes(self, exclude_signature: Optional[bool] = False) -> bytes:
        return self.to_json(exclude_signature=exclude_signature).encode('utf-8')
    
    def __eq__(self, other: 'Transaction') -> bool:
        return self.__dict__ == other.__dict__
    

def transaction_from_dict(transaction_data: Mapping[str, Any]) -> Transaction:
    if 'signature' in transaction_data:
        sig = transaction_data['signature']
    else:
        sig = None
    return Transaction(
        sender_address=transaction_data['sender'],
        recipient_address=transaction_data['recipient'],
        amount=transaction_data['amount'],
        signature=sig,
        timestamp=transaction_data['timestamp']
    )


def check_transaction_signature(transaction: Transaction) -> bool:
    key = RSA.import_key(transaction.get_sender_address())
    hashed_transaction = SHA256.new(transaction.to_bytes(exclude_signature=True))
    signature = bytes.fromhex(transaction.get_signature())
    try:
        pkcs1_15.new(key).verify(
            hashed_transaction,
            signature
        )
        return True
    except (ValueError, TypeError) as e:
        print(e)
        return False
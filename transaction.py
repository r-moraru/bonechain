from typing import Optional
import json

class Transaction:
    def __init__(
            self,
            sender_address: str,
            recipient_address: str,
            amount: int,
            signature: Optional[str] = None):
        self._sender_address = sender_address
        self._recipient_address = recipient_address
        self._amount = amount
        self._signature = signature

    def get_sender_address(self) -> str:
        return self._sender_address
    
    def get_recipient_address(self) -> str:
        return self._recipient_address
    
    def get_amount(self) -> int:
        return self._amount
    
    def get_signature(self) -> str:
        return self._signature

    def add_signature(self, signature: str):
        self._signature = signature

    def to_json(self, exclude_signature: Optional[bool] = False) -> str:
        transaction_data = {
            "sender": self._sender_address,
            "recipient": self._recipient_address,
            "amount": self._amount
        }

        if self._signature and not exclude_signature:
            transaction_data["signature"] = self._signature

        return json.dumps(transaction_data)
    
    def to_bytes(self, exclude_signature: Optional[bool] = False) -> bytes:
        return self.to_json(exclude_signature=exclude_signature).encode('utf-8')

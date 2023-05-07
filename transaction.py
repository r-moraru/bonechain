import json

class Transaction:
    def __init__(self, sender_address: str, recipient_address: str, amount: int):
        self._sender_address = sender_address
        self._recipient_address = recipient_address
        self._amount = amount
        self._signature = None

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

    def to_json(self) -> str:
        transaction_data = {
            "sender": self._sender_address,
            "recipient": self._recipient_address,
            "amount": self._amount
        }

        if self._signature:
            transaction_data["signature"] = self._signature

        return json.dumps(transaction_data)
    
    def to_bytes(self) -> bytes:
        return self.to_json().encode('utf-8')

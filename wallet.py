import binascii
import requests
from typing import Iterable, Optional
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from transaction import Transaction

class Wallet:
    def __init__(self, bootstrap_nodes: Optional[Iterable[str]] = None):
        self._private_key = RSA.generate(2048)
        self._public_key = self._private_key.publickey().export_key()
        self._bootstrap_nodes = bootstrap_nodes

    def get_public_key(self) -> RSA.RsaKey:
        return self._public_key

    def get_signed_transaction(self, transaction: Transaction) -> Transaction:
        transaction_data = transaction.to_bytes()
        hashed_transaction = SHA256.new(transaction_data)
        signature = pkcs1_15.new(self._private_key).sign(hashed_transaction)
        transaction.add_signature(binascii.hexlify(signature).decode("utf-8"))
        return transaction

    def request_transaction(self, recipient_address: str, amount: int) -> bool:
        new_transaction = Transaction(
            str(self._public_key),
            str(recipient_address),
            amount
        )

        signed_transaction = self.get_signed_transaction(new_transaction)
        signed_transaction_data = signed_transaction.to_json()

        # Try to send transaction to a listening node
        for bootstrap_node in self._bootstrap_nodes:
            response = requests.post(
                bootstrap_node,
                data={'transaction': signed_transaction_data}
            )

            if response.status_code == 200:
                break
        else:
            print("Unable to send transaction request to any of the bootstrap nodes.")
            return False

        return True

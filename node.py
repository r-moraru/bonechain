from typing import Iterable, Optional
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from transaction import Transaction

class Node:
    def __init__(
            self,
            ip: Optional[str] = None,
            consensus_port: Optional[int] = None,
            execution_port: Optional[int] = None,
            bootstrap_nodes: Optional[Iterable[str]] = None):
        self._ip = ip
        self._consensus_port = consensus_port
        self._execution_port = execution_port
        self._private_key = RSA.generate(2048)
        self._public_key = self._private_key.publickey().export_key()
        self._bootstrap_nodes = bootstrap_nodes

    def check_transaction_signature(self, transaction: Transaction) -> bool:
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
            return False
        
    def check_transaction_funds(self, transaction: Transaction) -> bool:
        pass

    def initialize_blockchain(self):
        pass

    def run_bootstrap_node(self):
        # TODO
        pass

    def join_network(self):
        # TODO: get peers using DHT, join gossip network
        pass
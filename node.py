from typing import Iterable, Optional
from Crypto.PublicKey import RSA

class Node:
    def __init__(self, bootstrap_nodes: Iterable[str]):
        self._url = None
        self._private_key = RSA.generate(2048)
        self._public_key = self._private_key.publickey().export_key()
        self._bootstrap_nodes = bootstrap_nodes
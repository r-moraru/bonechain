import binascii
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import json
from typing import Mapping, Any

class Validator:
    def __init__(
            self,):
        self._private_key = RSA.generate(2048)
        self._public_key = self._private_key.publickey().export_key().decode('utf-8')

    def get_public_key(self) -> str:
        return self._public_key

    def sign_message(self, message: Mapping[str, Any]) -> str:
        message_data = json.dumps(message)
        encoded_message = message_data.encode('utf-8')
        hashed_message = SHA256.new(encoded_message)
        signature = pkcs1_15.new(self._private_key).sign(hashed_message)
        return binascii.hexlify(signature).decode("utf-8")
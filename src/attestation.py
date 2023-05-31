
import json
from typing import Mapping, Any
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


class Attestation:
    def __init__(
            self,
            verdict: bool,
            block_hash: str,
            validator_id: str
            ):
        self._verdict = verdict
        self._block_hash = block_hash
        self._validator_id = validator_id
    
    def to_dict(self):
        return {
            'verdict': self._verdict,
            'block-hash': self._block_hash,
            'validator-id': self._validator_id
        }
    
    def to_json(self):
        data = self.to_dict()
        return json.dumps(data)

    def to_bytes(self):
        return self.to_json().encode('utf-8')


def attestation_from_dict(attestation_data: Mapping[str, Any]) -> Attestation:
    return Attestation(
        verdict=attestation_data['verdict'],
        block_hash=attestation_data['block-hash'],
        validator_id=attestation_data['validator-id']
    )

    
def check_attestation_signature(attestation: Attestation, signature: str) -> bool:
    key = RSA.import_key(attestation._validator_id)
    hashed_attestation = SHA256.new(attestation.to_bytes())
    signature = bytes.fromhex(signature)
    try:
        pkcs1_15.new(key).verify(
            hashed_attestation,
            signature
        )
        return True
    except (ValueError, TypeError) as e:
        return False

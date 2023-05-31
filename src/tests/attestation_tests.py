import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from attestation import Attestation, attestation_from_dict, check_attestation_signature
from validator import Validator

def test_attestation_to_dict():
    attestation = Attestation(
        verdict=True,
        block_hash='block-hash',
        validator_id='test-validator'
    )

    print("Attestation __dict__")
    print(attestation.__dict__)

    print("Attestation to dict()")
    print(attestation.to_dict())

def test_attesation_from_dict():
    attestation_data = {'verdict': True, 'block-hash': 'block-hash', 'validator-id': 'test-validator'}
    print("attestation data")
    print(attestation_data)

    print("attestation __dict__")
    print(attestation_from_dict(attestation_data).__dict__)

def test_attestation_signature():
    validator = Validator()
    attestation = Attestation(
        verdict=True,
        block_hash='block-hash',
        validator_id=validator.get_public_key()
    )
    signature = validator.sign_message(attestation.to_dict())
    if check_attestation_signature(attestation, signature):
        print("Signature is valid")
    else:
        print("Signature is invalid")


if __name__ == "__main__":
    print("-----------------------------ATTESTATION TO DICT-------------------------")
    test_attestation_to_dict()
    print("-----------------------------ATTESTATION FROM DICT-----------------------")
    test_attesation_from_dict()
    print("-----------------------------ATTESTATION SIGNATURE CHECK-----------------")
    test_attestation_signature()
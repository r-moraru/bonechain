import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from transaction import Transaction, check_transaction_signature
from wallet import Wallet
from block import Block

def wallet_tests():
    wallet1 = Wallet()
    wallet2 = Wallet()

    transaction = Transaction(
        wallet1.get_public_key(),
        wallet2.get_public_key(),
        10
    )

    signed_transaction = wallet1.get_signed_transaction(transaction)

    print("Unsigned transaction:")
    print(transaction.to_json())

    print("Signed transaction:")
    print(signed_transaction.to_json())


def node_signature_check():
    wallet1 = Wallet()
    wallet2 = Wallet()

    transaction = Transaction(
        wallet1.get_public_key(),
        wallet2.get_public_key(),
        10
    )

    signed_transaction = wallet1.get_signed_transaction(transaction)
    status1 = check_transaction_signature(signed_transaction)

    print('Transaction 1 signature is valid: ', status1)

    # Tamper with transaction
    signed_transaction._amount = 20
    status2 = check_transaction_signature(signed_transaction)

    print('Tampered with transaction after being signed.')
    print('Transaction is valid after being tampered with:', status2)

if __name__ == "__main__":
    print("---------------WALLET TESTS----------------")
    wallet_tests()
    print("-----------NODE SIGNATURE CHECK------------")
    node_signature_check()

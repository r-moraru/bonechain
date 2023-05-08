from transaction import Transaction
from wallet import Wallet
from block import Block
from node import Node

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

def send_transaction():
    node_url = "http://192.168.0.136:5000"
    wallet1 = Wallet([node_url])
    wallet2 = Wallet()

    if wallet1.request_transaction(str(wallet2.get_public_key()), 10):
        print('Transaction sent successfully.')

def node_signature_check():
    wallet1 = Wallet()
    wallet2 = Wallet()
    node1 = Node()

    transaction = Transaction(
        wallet1.get_public_key(),
        wallet2.get_public_key(),
        10
    )

    signed_transaction = wallet1.get_signed_transaction(transaction)
    status1 = node1.check_transaction_signature(signed_transaction)

    print('Transaction 1 signature is valid: ', status1)

    # Tamper with transaction
    signed_transaction._amount = 20
    status2 = node1.check_transaction_signature(signed_transaction)

    print('Tampered with transaction after being signed.')
    print('Transaction is valid after being tampered with:', status2)

def block_tests():
    wallet1 = Wallet()
    wallet2 = Wallet()
    transactions = [
        Transaction(
            wallet1.get_public_key(),
            wallet2.get_public_key(),
            10
        ),
        Transaction(
            wallet2.get_public_key(),
            wallet1.get_public_key(),
            10
        )
    ]
    
    block1 = Block("", transactions)

    print("Block1 hash:")
    print(block1.calculate_hash())

if __name__ == "__main__":
    print("---------------WALLET TESTS----------------")
    wallet_tests()
    print("----------------BLOCK TESTS----------------")
    block_tests()
    print("------------TRANSACTION TESTS--------------")
    send_transaction()
    print("-----------NODE SIGNATURE CHECK------------")
    node_signature_check()

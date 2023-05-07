from transaction import Transaction
from wallet import Wallet
from block import Block

def wallet_tests():
    wallet1 = Wallet()
    wallet2 = Wallet()

    transaction = Transaction(
        str(wallet1.get_public_key()),
        str(wallet2.get_public_key()),
        10
    )

    signed_transaction = wallet1.get_signed_transaction(transaction)

    print("Unsigned transaction:")
    print(transaction.to_json())

    print("Signed transaction:")
    print(signed_transaction.to_json())

def block_tests():
    wallet1 = Wallet()
    wallet2 = Wallet()
    transactions = [
        Transaction(
            str(wallet1.get_public_key()),
            str(wallet2.get_public_key()),
            10
        ),
        Transaction(
            str(wallet2.get_public_key()),
            str(wallet1.get_public_key()),
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

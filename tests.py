from transaction import Transaction
from wallet import Wallet

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

if __name__ == "__main__":
    wallet_tests()
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from block import Block, block_from_dict, Penalty, penalty_from_dict
from transaction import transaction_from_dict, Transaction
from wallet import Wallet
from datetime import datetime

def test_block_to_dict():
    block = Block(
        'test-forger',
        'previous-hash',
        datetime.now().timestamp(),
        transactions=[Transaction('s1', 'r1', 1), Transaction('s2', 'r2', 2)],
        join_requests=[Transaction('s1', 'v1', 0), Transaction('s2', 'v2', 0)],
        penalties=[Penalty(datetime.now().timestamp(), 'v0')]
    )

    print("Block __dict__:")
    print(block.__dict__)

    print("Block.to_dict()")
    print(block.to_dict())

def test_block_hash():
    block = Block(
        'test-forger',
        'previous-hash',
        datetime.now().timestamp(),
        transactions=[Transaction('s1', 'r1', 1), Transaction('s2', 'r2', 2)],
        join_requests=[Transaction('s1', 'v1', 0), Transaction('s2', 'v2', 0)],
        penalties=[Penalty(datetime.now().timestamp(), 'v0')]
    )

    print("Block hash:")
    print(block.calculate_hash())

def test_block_from_dict():
    block_data = {
        'timestamp': 1685485400.922484,
        'previous-hash': 'previous-hash',
        'forger-id': 'test-forger',
        'transactions': [
            {'timestamp': 1685485400.922493, 'sender': 's1', 'recipient': 'r1', 'amount': 1, 'signature': 'sig'},
            {'timestamp': 1685485400.922496, 'sender': 's2', 'recipient': 'r2', 'amount': 2, 'signature': 'sig'}],
        'penalties': [{'timestamp': 1685485400.922502, 'validator-id': 'v0'}],
        'join-requests': [
            {'timestamp': 1685485400.922498, 'sender': 's1', 'recipient': 'v1', 'amount': 0, 'signature': 'sig'},
            {'timestamp': 1685485400.9225, 'sender': 's2', 'recipient': 'v2', 'amount': 0, 'signature': 'sig'}]
    }

    print("Block data:")
    print(block_data)

    block = block_from_dict(block_data)
    print("Block.__dict__")
    print(block.__dict__)

    print("Transaction dicts")
    for transaction in block._transactions:
        print(transaction.__dict__)

    print('Join request dicts')
    for join_request in block._join_requests:
        print(join_request.__dict__)

    print('Penalty dicts')
    for penalty in block._penalties:
        print(penalty.__dict__)


if __name__ == "__main__":
    print("---------------------BLOCK TO DICT----------------------")
    test_block_to_dict()

    print("---------------------BLOCK HASH-------------------------")
    test_block_hash()

    print("--------------------BLOCK FROM DICT---------------------")
    test_block_from_dict()
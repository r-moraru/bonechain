import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from execution_layer import *
from ipcqueue import sysvmq
from multiprocessing import *

import time

def run_execution_layer(exec_layer: ExecutionLayer):
    exec_layer.run()

def test_blockchain_initialization():
    consensus_loop_out = sysvmq.Queue()
    consensus_loop_in = sysvmq.Queue()
    parent_in = sysvmq.Queue()
    parent_out = sysvmq.Queue()
    network_in = sysvmq.Queue()
    network_out = sysvmq.Queue()
    exec_layer = ExecutionLayer(
        validator=Validator(),
        wallet=Wallet(),
        consensus_loop_in=consensus_loop_out,
        consensus_loop_out=consensus_loop_in,
        network_in=network_out,
        network_out=network_in,
        parent_in=parent_out,
        parent_out=parent_in,
        is_blockchain_creator=True
    )

    p1 = Process(target=run_execution_layer, args=(exec_layer,))
    p1.start()

    network_out.put(
        {
            'sender-address': '1111'
        },
        block=True,
        msg_type=network_message_types['blockchain']
    )

    answer = network_in.get(
        block=True,
        msg_type=network_message_types['blockchain']
    )

    timestamp = parent_in.get(
        block=True,
        msg_type=parent_message_types['genesis-timestamp']
    )

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['stop']
    )

    p1.join()

    print(answer)
    print('creation timestamp:', timestamp)


def test_forger_id_for_single_node():
    consensus_loop_out = sysvmq.Queue()
    consensus_loop_in = sysvmq.Queue()
    parent_in = sysvmq.Queue()
    parent_out = sysvmq.Queue()
    network_in = sysvmq.Queue()
    network_out = sysvmq.Queue()
    wallet1 = Wallet()
    exec_layer = ExecutionLayer(
        validator=Validator(),
        wallet=wallet1,
        consensus_loop_in=consensus_loop_out,
        consensus_loop_out=consensus_loop_in,
        network_in=network_out,
        network_out=network_in,
        parent_in=parent_out,
        parent_out=parent_in,
        is_blockchain_creator=True
    )

    p1 = Process(target=run_execution_layer, args=(exec_layer,))
    p1.start()

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['forger-id']
    )

    forger_id = consensus_loop_in.get(
        block=True,
        msg_type=consensus_message_types['forger-id']
    )

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['stop']
    )

    p1.join()

    assert forger_id == exec_layer._validator.get_public_key()
    print("test passed.")


def single_node_transaction_test():
    consensus_loop_out = sysvmq.Queue()
    consensus_loop_in = sysvmq.Queue()
    parent_in = sysvmq.Queue()
    parent_out = sysvmq.Queue()
    network_in = sysvmq.Queue()
    network_out = sysvmq.Queue()
    wallet1 = Wallet()
    wallet2 = Wallet()
    exec_layer = ExecutionLayer(
        validator=Validator(),
        wallet=wallet1,
        consensus_loop_in=consensus_loop_out,
        consensus_loop_out=consensus_loop_in,
        network_in=network_out,
        network_out=network_in,
        parent_in=parent_out,
        parent_out=parent_in,
        is_blockchain_creator=True
    )

    p1 = Process(target=run_execution_layer, args=(exec_layer,))
    p1.start()
    
    transaction = Transaction(
            wallet1.get_public_key(),
            wallet2.get_public_key(),
            amount=100
        )
    signed_transaction = wallet1.get_signed_transaction(transaction)
    network_out.put(
        signed_transaction.to_dict(),
        block=True,
        msg_type=network_message_types['transaction']
    )

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['forger-id']
    )

    time.sleep(1)

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['create-block']
    )

    time.sleep(0.5)

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['end-cycle']
    )

    time.sleep(0.5)

    network_out.put(
        {
            'sender-address': '1111',
        },
        block=True,
        msg_type=network_message_types['blockchain']
    )

    answer = network_in.get(
        block=True,
        msg_type=network_message_types['blockchain']
    )

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['stop']
    )

    assert len(answer['blockchain']) == 2
    assert len(answer['blockchain'][1]['transactions']) == 1
    print(answer['blockchain'][1]['transactions'][0])
    print('test passed.')


def single_node_transaction_acc_ref():
    consensus_loop_out = sysvmq.Queue()
    consensus_loop_in = sysvmq.Queue()
    parent_in = sysvmq.Queue()
    parent_out = sysvmq.Queue()
    network_in = sysvmq.Queue()
    network_out = sysvmq.Queue()
    wallet1 = Wallet()
    wallet2 = Wallet()
    exec_layer = ExecutionLayer(
        validator=Validator(),
        wallet=wallet1,
        consensus_loop_in=consensus_loop_out,
        consensus_loop_out=consensus_loop_in,
        network_in=network_out,
        network_out=network_in,
        parent_in=parent_out,
        parent_out=parent_in,
        is_blockchain_creator=True
    )

    p1 = Process(target=run_execution_layer, args=(exec_layer,))
    p1.start()
    
    transaction = Transaction(
        wallet1.get_public_key(),
        wallet2.get_public_key(),
        amount=100
    )
    signed_transaction = wallet1.get_signed_transaction(transaction)

    transaction2 = Transaction(
        wallet2.get_public_key(),
        wallet1.get_public_key(),
        amount=101
    )
    signed_transaction2 = wallet2.get_signed_transaction(transaction2)
    network_out.put(
        signed_transaction.to_dict(),
        block=True,
        msg_type=network_message_types['transaction']
    )

    network_out.put(
        signed_transaction2.to_dict(),
        block=True,
        msg_type=network_message_types['transaction']
    )

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['forger-id']
    )

    time.sleep(1)

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['create-block']
    )

    time.sleep(0.5)

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['end-cycle']
    )

    time.sleep(0.5)

    network_out.put(
        {
            'sender-address': '1111',
        },
        block=True,
        msg_type=network_message_types['blockchain']
    )

    answer = network_in.get(
        block=True,
        msg_type=network_message_types['blockchain']
    )

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['stop']
    )

    assert len(answer['blockchain']) == 2
    assert len(answer['blockchain'][1]['transactions']) == 1
    print(answer['blockchain'][1]['transactions'][0])
    print('test passed.')


def single_node_two_blocks_transaction_acc_ref():
    consensus_loop_out = sysvmq.Queue()
    consensus_loop_in = sysvmq.Queue()
    parent_in = sysvmq.Queue()
    parent_out = sysvmq.Queue()
    network_in = sysvmq.Queue()
    network_out = sysvmq.Queue()
    wallet1 = Wallet()
    wallet2 = Wallet()
    exec_layer = ExecutionLayer(
        validator=Validator(),
        wallet=wallet1,
        consensus_loop_in=consensus_loop_out,
        consensus_loop_out=consensus_loop_in,
        network_in=network_out,
        network_out=network_in,
        parent_in=parent_out,
        parent_out=parent_in,
        is_blockchain_creator=True
    )

    p1 = Process(target=run_execution_layer, args=(exec_layer,))
    p1.start()
    
    transaction = Transaction(
        wallet1.get_public_key(),
        wallet2.get_public_key(),
        amount=100
    )
    signed_transaction = wallet1.get_signed_transaction(transaction)
    network_out.put(
        signed_transaction.to_dict(),
        block=True,
        msg_type=network_message_types['transaction']
    )

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['forger-id']
    )

    time.sleep(0.7)

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['create-block']
    )

    time.sleep(0.5)

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['end-cycle']
    )

    time.sleep(0.5)

    transaction2 = Transaction(
        wallet1.get_public_key(),
        wallet2.get_public_key(),
        amount=generator_wallet_amount-99
    )
    signed_transaction2 = wallet1.get_signed_transaction(transaction2)
    network_out.put(
        signed_transaction2.to_dict(),
        block=True,
        msg_type=network_message_types['transaction']
    )

    time.sleep(0.5)

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['forger-id']
    )
    time.sleep(0.7)

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['create-block']
    )

    time.sleep(0.5)

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['end-cycle']
    )

    time.sleep(0.5)

    network_out.put(
        {
            'sender-address': '1111',
        },
        block=True,
        msg_type=network_message_types['blockchain']
    )

    answer = network_in.get(
        block=True,
        msg_type=network_message_types['blockchain']
    )

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['stop']
    )

    assert len(answer['blockchain']) == 3
    assert len(answer['blockchain'][1]['transactions']) == 1
    assert len(answer['blockchain'][2]['transactions']) == 0
    print(answer['blockchain'][1]['transactions'])
    print(answer['blockchain'][2]['transactions'])
    print('test passed.')


def single_node_transaction_two_acc():
    consensus_loop_out = sysvmq.Queue()
    consensus_loop_in = sysvmq.Queue()
    parent_in = sysvmq.Queue()
    parent_out = sysvmq.Queue()
    network_in = sysvmq.Queue()
    network_out = sysvmq.Queue()
    wallet1 = Wallet()
    wallet2 = Wallet()
    exec_layer = ExecutionLayer(
        validator=Validator(),
        wallet=wallet1,
        consensus_loop_in=consensus_loop_out,
        consensus_loop_out=consensus_loop_in,
        network_in=network_out,
        network_out=network_in,
        parent_in=parent_out,
        parent_out=parent_in,
        is_blockchain_creator=True
    )

    p1 = Process(target=run_execution_layer, args=(exec_layer,))
    p1.start()
    
    transaction = Transaction(
        wallet1.get_public_key(),
        wallet2.get_public_key(),
        amount=100
    )
    signed_transaction = wallet1.get_signed_transaction(transaction)

    transaction2 = Transaction(
        wallet2.get_public_key(),
        wallet1.get_public_key(),
        amount=50
    )
    signed_transaction2 = wallet2.get_signed_transaction(transaction2)
    network_out.put(
        signed_transaction.to_dict(),
        block=True,
        msg_type=network_message_types['transaction']
    )

    network_out.put(
        signed_transaction2.to_dict(),
        block=True,
        msg_type=network_message_types['transaction']
    )

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['forger-id']
    )

    time.sleep(2)

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['create-block']
    )

    time.sleep(0.5)

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['end-cycle']
    )

    time.sleep(0.5)

    network_out.put(
        {
            'sender-address': '1111',
        },
        block=True,
        msg_type=network_message_types['blockchain']
    )

    answer = network_in.get(
        block=True,
        msg_type=network_message_types['blockchain']
    )

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['stop']
    )

    assert len(answer['blockchain']) == 2
    assert len(answer['blockchain'][1]['transactions']) == 2
    print(answer['blockchain'][1]['transactions'])
    print('test passed.')

def two_validators_join():
    consensus_loop_out = sysvmq.Queue()
    consensus_loop_in = sysvmq.Queue()
    parent_in = sysvmq.Queue()
    parent_out = sysvmq.Queue()
    network_in = sysvmq.Queue()
    network_out = sysvmq.Queue()
    wallet1 = Wallet()
    wallet2 = Wallet()
    exec_layer = ExecutionLayer(
        validator=Validator(),
        wallet=wallet1,
        consensus_loop_in=consensus_loop_out,
        consensus_loop_out=consensus_loop_in,
        network_in=network_out,
        network_out=network_in,
        parent_in=parent_out,
        parent_out=parent_in,
        is_blockchain_creator=True
    )

    consensus_loop_out2 = sysvmq.Queue()
    consensus_loop_in2 = sysvmq.Queue()
    parent_in2 = sysvmq.Queue()
    parent_out2 = sysvmq.Queue()
    network_in2 = sysvmq.Queue()
    network_out2 = sysvmq.Queue()
    exec_layer2 = ExecutionLayer(
        validator=Validator(),
        wallet=wallet2,
        consensus_loop_in=consensus_loop_out2,
        consensus_loop_out=consensus_loop_in2,
        network_in=network_out2,
        network_out=network_in2,
        parent_in=parent_out2,
        parent_out=parent_in2,
        is_blockchain_creator=False
    )

    p1 = Process(target=run_execution_layer, args=(exec_layer,))
    p1.start()
    
    transaction = Transaction(
        wallet1.get_public_key(),
        wallet2.get_public_key(),
        amount=100
    )
    signed_transaction = wallet1.get_signed_transaction(transaction)
    network_out.put(
        signed_transaction.to_dict(),
        block=True,
        msg_type=network_message_types['transaction']
    )

    p2 = Process(target=run_execution_layer, args=(exec_layer2,))
    p2.start()

    join_request = network_in2.get(
        block=True,
        msg_type=network_message_types['join-request']
    )
    network_out.put(
        join_request,
        block=True,
        msg_type=network_message_types['join-request']
    )

    blockchain_request = network_in2.get(
        block=True,
        msg_type=network_message_types['blockchain']
    )
    network_out.put(
        blockchain_request,
        block=True,
        msg_type=network_message_types['blockchain']
    )
    blockchain = network_in.get(
        block=True,
        msg_type=network_message_types['blockchain']
    )
    network_out2.put(
        blockchain,
        block=True,
        msg_type=network_message_types['blockchain']
    )

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['forger-id']
    )

    time.sleep(0.5)

    consensus_loop_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['create-block']
    )

    time.sleep(0.5)

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['end-cycle']
    )

    time.sleep(0.5)

    network_out.put(
        {
            'sender-address': '1111',
        },
        block=True,
        msg_type=network_message_types['blockchain']
    )

    answer = network_in.get(
        block=True,
        msg_type=network_message_types['blockchain']
    )

    parent_out.put(
        True,
        block=True,
        msg_type=parent_message_types['stop']
    )

    parent_out2.put(
        True,
        block=True,
        msg_type=parent_message_types['stop']
    )

    p1.join()
    p2.join()

    assert len(answer['blockchain']) == 2
    assert len(answer['blockchain'][1]['transactions']) == 1
    assert len(answer['blockchain'][1]['join-requests']) == 1
    print('PERSISTED JOIN REQUEST:', answer['blockchain'][1]['join-requests'])
    print('test passed.')


if __name__ == "__main__":
    print("---------------------BLOCKCHAIN INIT------------------")
    test_blockchain_initialization()

    print("---------------------SINGLE NODE FORGER ID------------")
    test_forger_id_for_single_node()

    print("------------------SINGLE NODE TRANSACTION-------------")
    single_node_transaction_test()

    print("----2 transactions per block, 2 accepted-------------")
    single_node_transaction_two_acc()

    print("---------testing balance updating inside block----------------")
    single_node_transaction_acc_ref()

    print("-----------testing balance updating between blocks-----------")
    single_node_two_blocks_transaction_acc_ref()

    print("-----------------TESTING JOIN FUNCTION-------------------")
    two_validators_join()

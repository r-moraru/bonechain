import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from execution_layer import *
from ipcqueue import sysvmq
from multiprocessing import *

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

    print("forger id:", forger_id)
    print("execution layer validator id:", exec_layer._validator.get_public_key())

    p1.join()


def transaction_test():
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
            wallet1,
            wallet2,
            amount=100
        )
    signed_transaction = wallet1.get_signed_transaction(transaction)
    network_out.put(
        signed_transaction,
        block=True,
        msg_type=network_message_types['transaction']
    )

    pass


if __name__ == "__main__":
    print("---------------------BLOCKHAIN INIT------------------")
    test_blockchain_initialization()

    print("---------------------SINGLE NODE FORGER ID-----------")
    test_forger_id_for_single_node()
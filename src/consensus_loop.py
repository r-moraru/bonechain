from ipcqueue import sysvmq

from blockchain import Blockchain
from execution_layer import Validator
from util import *

def consensus_loop(
        validator: Validator,
        execution_layer_in: sysvmq.Queue,
        execution_layer_out: sysvmq.Queue,
        network_in: sysvmq.Queue,
        network_out: sysvmq.Queue):
    execution_layer_out.put(
        True,
        block=True,
        msg_type=consensus_message_types['forger-id']
    )

    forger_id = execution_layer_in.get(
        block=True,
        msg_type=consensus_message_types['forger-id']
    )

    if forger_id == validator.get_public_key():
        execution_layer_out.put(
            True,
            block=True,
            msg_type=consensus_message_types['create-block']
        )

        block = execution_layer_in.get(
            True,
            block=True,
            msg_type=consensus_message_types['create-block']
        )

        network_out.put(
            block,
            block=True,
            msg_type=network_message_types['create-block']
        )
    else:
        # Listen for all incoming blocks and send them for checking.
        # Continue to listen after finding a valid block from the forger
        # in order to catch bad nodes.
        while True:
            block = network_in.get(
                block=True,
                msg_type=network_message_types['create-block']
            )

            block_check_request = {
                'block': block
            }

            execution_layer_out.put(
                block_check_request,
                block=True,
                msg_type=consensus_message_types['check-block']
            )
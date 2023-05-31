from ipcqueue import sysvmq
import itertools
import json
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from datetime import datetime
import random
from typing import Iterable, Mapping, Any

from attestation import Attestation, attestation_from_dict, check_attestation_signature
from block import Block, Penalty, block_from_dict
from blockchain import Blockchain
from transaction import Transaction, check_transaction_signature, transaction_from_dict
from util import *
from validator import Validator
from wallet import Wallet


class ExecutionLayer:
    def __init__(
            self,
            validator: Validator,
            wallet: Wallet,
            consensus_loop_in: sysvmq.Queue,
            consensus_loop_out: sysvmq.Queue,
            network_in: sysvmq.Queue,
            network_out: sysvmq.Queue,
            parent_in: sysvmq.Queue,
            parent_out: sysvmq.Queue,
            is_blockchain_creator: bool = False):
        self._validator = validator
        self._wallet = wallet
        self._is_blockchain_creator = is_blockchain_creator

        self._consensus_loop_in = consensus_loop_in
        self._consensus_loop_out = consensus_loop_out
        self._network_in = network_in
        self._network_out = network_out
        self._parent_in = parent_in
        self._parent_out = parent_out

        self._blockchain = None

        self._proposed_block = None
        self._proposed_forger = None
        self._attestation_pool = {}
        self._account_balances = {}
        self._validator_wallets = {}
        self._penalty_pool = []
        self._joining_pool = []
        self._pending_transactions = []

    def reverse_transaction(self, transaction: Transaction):
        self._account_balances[transaction.get_sender_address()] += transaction.get_amount()
        self._account_balances[transaction.get_recipient_address()] -= transaction.get_amount()

    def update_state_from_transaction(self, transaction: Transaction, is_from_genesis: bool = False):
        if transaction.get_recipient_address() not in self._account_balances:
            self._account_balances[transaction.get_recipient_address()] = 0
        if not is_from_genesis:
            self._account_balances[transaction.get_sender_address()] -= transaction.get_amount()
        self._account_balances[transaction.get_recipient_address()] += transaction.get_amount()

    def update_state_from_join_request(self, join_request: Transaction):
        self._validator_wallets[join_request.get_recipient_address()] = join_request.get_sender_address()

    def reverse_join_request(self, join_request: Transaction):
        self._validator_wallets.pop(join_request.get_recipient_address())

    def update_state_from_penalty(self, penalty: Penalty):
        wallet_address = self._validator_wallets[penalty.get_validator_id()]
        self._account_balances[wallet_address] -= self._account_balances[wallet_address] * penalty_percentage

    def update_state_from_block(self, block: Block, is_from_genesis: bool = False):
        i, j, k = 0, 0, 0

        while True:
            if i == len(block._transactions) and j == len(block._join_requests) and k == len(block._penalties):
                return
            sentinel = datetime.now().timestamp() + 5
            if i == len(block._transactions):
                transaction_time = sentinel
            else:
                transaction_time = block._transactions[i].get_timestamp()
            if j == len(block._join_requests):
                join_time = sentinel
            else:
                join_time = block._join_requests[j].get_timestamp()
            if k == len(block._penalties):
                penalty_time = sentinel
            else:
                penalty_time = block._penalties[k].get_timestamp()

            if transaction_time <= join_time and transaction_time <= penalty_time:
                self.update_state_from_transaction(block._transactions[i], is_from_genesis=is_from_genesis)
                i += 1
            if join_time <= transaction_time and join_time <= penalty_time:
                self.update_state_from_join_request(block._join_requests[j])
                j += 1
            if penalty_time <= transaction_time and penalty_time <= join_time:
                self.update_state_from_penalty(block._penalties[k])
                k += 1

    def update_state_from_blockchain(self):
        self.update_state_from_block(
            self._blockchain.get_blocks()[0],
            is_from_genesis=True)
        for block in self._blockchain.get_blocks()[1:]:
            self.update_state_from_block(block)

    def create_join_request(self, wallet: Wallet):
        transaction = Transaction(
            wallet.get_public_key(),
            self._validator.get_public_key(),
            0)
        signed_transaction = wallet.get_signed_transaction(transaction)

        return signed_transaction

    def join_network(
            self,
            is_blockchain_creator: bool,
            wallet: Wallet):
        join_request = self.create_join_request(wallet)

        if is_blockchain_creator:
            # OPT: save all wallets somewhere
            wallet1 = Wallet()
            self._blockchain = Blockchain()
            # for simplicity, add a transaction and a join request to be
            # processed but not checked by the rest of the nodes
            self._blockchain.add_block(
                Block(
                    forger_id=self._validator.get_public_key(),
                    timestamp=datetime.now().timestamp(),
                    previous_hash='',
                    transactions=[
                        Transaction(
                            sender_address='',
                            recipient_address=wallet.get_public_key(),
                            amount=generator_wallet_amount
                        ),
                        Transaction(
                            sender_address=wallet.get_public_key(),
                            recipient_address=wallet1.get_public_key(),
                            amount=2 * minimum_validator_balance
                        )
                    ],
                    join_requests=[
                        self.create_join_request(wallet1)
                    ],
                    penalties=[]
                )
            )

            self._parent_out.put(
                self._blockchain.get_blocks()[0]._timestamp,
                block=True,
                msg_type=parent_message_types['genesis-timestamp']
            )
        else:
            self._network_out.put(
                join_request.to_dict(),
                block=True,
                msg_type=network_message_types['join-request']
            )

            self._network_out.put(
                {
                    'sender-id': self._validator.get_public_key()
                },
                block=True,
                msg_type=network_message_types['blockchain']
            )

            blockchain = self._network_in.get(
                block=True,
                msg_type=network_message_types['blockchain']
            )
            blockchain = [block_from_dict(block_data) for block_data in blockchain]

            # suppose bootstrap nodes in network send honest blockchains
            self._blockchain = blockchain

            self._parent_out.put(
                self._blockchain.get_blocks()[0]._timestamp,
                block=True,
                msg_type=parent_message_types['genesis-timestamp']
            )

        self.update_state_from_blockchain()

    def check_transaction_funds(self, transaction: Transaction):
        sender = transaction.get_sender_address()
        if self._account_balances[sender] < transaction.get_amount():
            return False
        return True

    def process_transaction(self, transaction: Transaction) -> bool:
        if transaction.get_sender_address() in self._validator_wallets.values():
            return False
        
        if (check_transaction_signature(transaction)):
            self._pending_transactions.append(transaction)
            return True
        return False

    def process_join_request(self, join_request: Transaction):
        # While percieved as validator, all transactions
        # made after this request from the wallet are ignored.
        # After x rounds of inactivity, wallet is freed again.
        valid = (
            check_transaction_signature(join_request) and
            join_request.get_sender_address() in self._account_balances.keys() and
            self._account_balances[join_request.get_sender_address()] >= minimum_validator_balance
        )
        if valid:
            self._joining_pool.append(join_request)

    def process_blockchain_request(self, blockchain_request):
        self._network_out.put(
            {
                'recipient-address': blockchain_request['sender-address'],
                'blockchain': [block.to_dict() for block in self._blockchain.get_blocks()]
            },
            block=False,
            msg_type=network_message_types['blockchain']
        )

    def process_attestation(self, attestation: Attestation, signature: str):
        if not attestation._validator_id in self._validator_wallets.keys():
            return

        if not check_attestation_signature(attestation, signature):
            return
        
        self._attestation_pool[attestation._validator_id] = attestation

    def get_total_stake(self):
        stake = 0
        for wallet in self._validator_wallets.values():
            stake += self._account_balances[wallet]

        return stake

    def get_forger_id(self):
        total_stake = self.get_total_stake()
        # OPT: improve randomizer
        validators = list(self._validator_wallets.keys())
        validator_wallets = list(self._validator_wallets.values())
        stake_percentages = [
            self._account_balances[wallet] / total_stake for wallet in validator_wallets
        ]

        stake_percentage_cdfs = list(itertools.accumulate(stake_percentages))

        random.seed(self._blockchain.get_blocks()[-1]._next_seed)
        random_value = random.random()

        for validator, stake_percentage_cdf in zip(validators, stake_percentage_cdfs):
            if stake_percentage_cdf >= random_value:
                return validator

    def process_forger_id_request(self):
        forger_id = self.get_forger_id()

        self._proposed_forger = forger_id
        
        self._consensus_loop_out.put(
            forger_id,
            block=False,
            msg_type=consensus_message_types['forger-id']
        )

    def filter_out_invalid_data(
            self,
            transactions: Iterable[Transaction],
            join_requests: Iterable[Transaction]) -> tuple[Iterable[Transaction]]:
        i, j = 0, 0
        accepted_transactions = []
        accepted_join_requests = []
        while True:
            sentinel = datetime.now().timestamp()+3
            if i == len(transactions) and j == len(join_requests):
                break
            if i == len(transactions):
                transaction_time = sentinel
            else:
                transaction_time = transactions[i].get_timestamp()
            
            if j == len(join_requests):
                join_request_time = sentinel
            else:
                join_request_time = join_requests[i].get_timestamp()

            if transaction_time < join_request_time:
                if (self.check_transaction_funds(transactions[i]) and
                    not transactions[i].get_sender_address() in self._validator_wallets.values()):
                    self.update_state_from_transaction(transactions[i])
                    accepted_transactions.append(transactions[i])
                i += 1
            else:
                # OPT: check for minimum validator balance
                self.update_state_from_join_request(join_requests[j])
                accepted_join_requests.append(join_requests[j])
                j += 1

        for transaction in accepted_transactions:
            self.reverse_transaction(transaction)
        
        for join_request in accepted_join_requests:
            self.reverse_join_request(join_request)

        return accepted_transactions, accepted_join_requests

    def get_valid_data(self, creation_time: float):
        block_transactions = [
            transaction for transaction in self._pending_transactions
            if transaction.get_timestamp() <= creation_time-ignore_time_delta
        ]
        block_join_requests = [
            join_request for join_request in self._joining_pool
            if join_request.get_timestamp() <= creation_time-ignore_time_delta
        ]
        block_penalties = self._penalty_pool

        block_transactions.sort(key=lambda x: x.get_timestamp())
        block_join_requests.sort(key=lambda x: x.get_timestamp())
        block_penalties.sort(key=lambda x: x.get_timestamp())

        filtered_transactions, filtered_join_requests = (
            self.filter_out_invalid_data(block_transactions, block_join_requests))

        return filtered_transactions, filtered_join_requests, block_penalties

    def process_block_creation_request(self):
        # OPT: also add signature
        if not self._validator.get_public_key() in self._validator_wallets.keys():
            return # Don't participate if not accepted yet

        creation_time = datetime.now().timestamp()
        
        last_block_hash = self._blockchain.get_blocks()[-1].calculate_hash()

        block_transactions, block_join_requests, block_penalties = self.get_valid_data(creation_time)

        new_block = Block(
            self._validator.get_public_key(),
            last_block_hash,
            creation_time,
            transactions=block_transactions,
            penalties=block_penalties,
            join_requests=block_join_requests
        )

        self._network_out.put(
            new_block.to_dict(),
            block=False,
            msg_type=network_message_types['create-block']
        )

        attestation = Attestation(
            verdict=True,
            block_hash=new_block.calculate_hash(),
            validator_id=self._validator.get_public_key()
        )

        self._attestation_pool[self._validator.get_public_key()] = attestation
        self._proposed_block = new_block

        attestation_signature = self._validator.sign_message(attestation.to_dict())

        answer = {
            'attestation': attestation.to_dict(),
            'signature': attestation_signature
        }

        self._network_out.put(
            answer,
            block=False,
            msg_type=network_message_types['attestation']
        )

    def check_block(self, block: Block) -> bool:
        # OPT: also check signatures
        if block._forger_id != self._proposed_forger:
            return False
        
        if block._previous_hash != self._blockchain.get_blocks()[-1].calculate_hash():
            return False
        
        if datetime.now().timestamp() - block._timestamp > 12 or block._timestamp > datetime.now().timestamp():
            return False
        
        valid_transactions, valid_join_requests, valid_penalties = self.get_valid_data(block._timestamp)

        if (block._transactions != valid_transactions or
            block._join_requests != valid_join_requests or
            block._penalties != valid_penalties):
            return False

        return True

    def process_block_check_request(self, block_check_request):
        verdict = self.check_block(block_check_request['block'])

        if verdict == True:
            self._proposed_block = block_check_request['block']

        if not self._validator.get_public_key() in self._validator_wallets.keys():
            return # Don't participate in consensus if not accepted yet

        attestation = Attestation(
            verdict=verdict,
            block_hash=block_check_request['block'].calculate_hash(),
            validator_id=self._validator.get_public_key()
        )

        self._attestation_pool[self._validator.get_public_key()] = attestation

        attestation_signature = self._validator.sign_message(attestation.to_dict())

        answer = {
            'attestation': attestation.to_dict(),
            'signature': attestation_signature
        }

        self._network_out.put(
            answer,
            block=False,
            msg_type=network_message_types['attestation']
        )

    def clear_data(self, block_creation_time: float):
        self._pending_transactions = [
            transaction for transaction in self._pending_transactions
            if transaction.get_timestamp() > block_creation_time-ignore_time_delta
        ]
        self._joining_pool = [
            join_request for join_request in self._joining_pool
            if join_request.get_timestamp() > block_creation_time-ignore_time_delta
        ]
        self._penalty_pool = []

    def check_proposed_block_validity(self):
        total_stake = self.get_total_stake()
        block_attestor_stake = 0
        for attestation in self._attestation_pool.values():
            if attestation._verdict == True:
                validator_wallet = self._validator_wallets[attestation._validator_id]
                block_attestor_stake += self._account_balances[validator_wallet]
        
        if block_attestor_stake/total_stake > 2/3:
            return True

    def process_inactive_validators(self):
        # Currently inactive validators simply get removed from the pool
        self._validator_wallets = {
            validator: wallet for validator, wallet in self._validator_wallets.items()
            if validator in self._attestation_pool
        }

    def process_end_cycle_request(self):
        if not self._proposed_block:
            if len(self._validator_wallets.keys()) > 1:
                self._penalty_pool.append(self._proposed_forger)

        self.process_inactive_validators()

        if self.check_proposed_block_validity():
            self._blockchain.add_block(self._proposed_block)
            self.update_state_from_block(self._proposed_block)
            self.clear_data(self._proposed_block._timestamp)
        else:
            self._penalty_pool.append(self._proposed_forger)

        self._proposed_block = None
        self._proposed_forger = None

    def run(self):
        self.join_network(
            self._is_blockchain_creator,
            self._wallet
        )
        while True:
            try:
                new_transaction = self._network_in.get(
                    block=False,
                    msg_type=network_message_types['transaction']
                )
                new_transaction = transaction_from_dict(new_transaction)
                self.process_transaction(new_transaction)
            except sysvmq.queue.Empty:
                pass

            try:
                join_request = self._network_in.get(
                    block=False,
                    msg_type=network_message_types['join-request']
                )
                join_request = transaction_from_dict(join_request)
                self.process_join_request(join_request)
            except sysvmq.queue.Empty:
                pass

            try:
                blockchain_request = self._network_in.get(
                    block=False,
                    msg_type=network_message_types['blockchain']
                )
                self.process_blockchain_request(blockchain_request)
            except sysvmq.queue.Empty:
                pass

            try:
                attestation = self._network_in.get(
                    block=False,
                    msg_type=network_message_types['attestation']
                )
                attestation = attestation_from_dict(attestation)
                self.process_attestation(attestation)
            except sysvmq.queue.Empty:
                pass

            # consensus requests
            try:
                self._consensus_loop_in.get(
                    block=False,
                    msg_type=consensus_message_types['forger-id']
                )
                self.process_forger_id_request()
            except sysvmq.queue.Empty:
                pass

            try:
                self._consensus_loop_in.get(
                    block=False,
                    msg_type=consensus_message_types['create-block']
                )
                self.process_block_creation_request()
            except sysvmq.queue.Empty:
                pass

            try:
                block_check_request = self._consensus_loop_in.get(
                    block=False,
                    msg_type=consensus_message_types['check-block']
                )
                block_check_request['block'] = block_from_dict(block_check_request['block'])
                self.process_block_check_request(block_check_request)
            except sysvmq.queue.Empty:
                pass

            try:
                self._parent_in.get(
                    block=False,
                    msg_type=parent_message_types['end-cycle']
                )
                self.process_end_cycle_request()
            except sysvmq.queue.Empty:
                pass

            try:
                self._parent_in.get(
                    block=False,
                    msg_type=parent_message_types['stop']
                )
                break
            except sysvmq.queue.Empty:
                pass

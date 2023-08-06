import os
import time

from web3 import Web3
from eth_account import Account, messages
import requests
import json
from typing import List, Union


class RevertedTx(Exception):
    pass


class TxExecutionError(Exception):
    pass


class FlashbotsRPC:
    def __init__(self, endpoint: str = "https://relay.flashbots.net"):
        self.endpoint = endpoint
        # TODO: get right env
        self.pk = os.environ["FLASHBOT_SIGNER_KEY"]

    def get_signature(self, body: dict) -> str:
        message = messages.encode_defunct(text=Web3.keccak(text=json.dumps(body)).hex())
        signature = (
            Account.from_key(self.pk).address
            + ":"
            + Account.sign_message(message, self.pk).signature.hex()
        )
        return signature

    def make_post_request(self, body: dict) -> Union[dict, None]:
        res = requests.post(
            url=self.endpoint,
            json=body,
            headers={
                "Content-Type": "application/json",
                "X-Flashbots-Signature": self.get_signature(body),
            },
        )
        if res.status_code == 200:
            return json.loads(res.text)

    def check_reverted(self, call_bundle_res):
        for tx in call_bundle_res["results"]:
            if "error" in tx and "execution reverted" in tx["error"]:
                raise RevertedTx(json.dumps(call_bundle_res))

    def send_bundle(self, txs: List[str], target_block: int) -> Union[dict, None]:
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [
                {
                    "txs": txs,
                    "blockNumber": hex(target_block),
                }
            ],
        }

        res = self.make_post_request(body)
        if res is None:
            return
        elif "error" in res:
            raise TxExecutionError(res["error"])
        # If result: https://docs.flashbots.net/flashbots-auction/searchers/advanced/rpc-endpoint#eth_sendbundle
        return res["result"]

    def call_bundle(
        self, txs: List[str], target_block: int, **kwargs
    ) -> Union[dict, None]:
        if "stateBlockNumber" not in kwargs:
            kwargs["stateBlockNumber"] = "latest"
        if "timestamp" not in kwargs:
            kwargs["timestamp"] = (
                int(time.time()) + 15
            )  # current time plus average block time

        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_callBundle",
            "params": [
                {
                    "txs": txs,
                    "blockNumber": hex(target_block),
                    "stateBlockNumber": kwargs["stateBlockNumber"],
                    "timestamp": kwargs["timestamp"],
                }
            ],
        }
        res = self.make_post_request(body)
        if res is None:
            return
        elif "error" in res:
            # If error: {'code': -32000, 'message': 'err: nonce too high: address 0x, tx: 32 state: 30; txhash 0x'}
            raise TxExecutionError(res["error"])
        # If result: https://docs.flashbots.net/flashbots-auction/searchers/advanced/rpc-endpoint#eth_callbundle
        # Revert data inside as well
        return res["result"]

    def get_bundle_stats(self, bundle_hash: str, block: int) -> Union[dict, None]:
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "flashbots_getBundleStats",
            "params": [
                {
                    "bundleHash": bundle_hash,
                    "blockNumber": hex(block),
                }
            ],
        }
        res = self.make_post_request(body)
        if res is None:
            return
        elif "error" in res:
            return res["error"]
        # https://docs.flashbots.net/flashbots-auction/searchers/advanced/rpc-endpoint#flashbots_getbundlestats
        return res["result"]

    def get_user_stats(self, block: int) -> Union[dict, None]:
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "flashbots_getUserStats",
            "params": [hex(block)],
        }
        res = self.make_post_request(body)
        if res is None:
            return
        elif "error" in res:
            return res["error"]
        # https://docs.flashbots.net/flashbots-auction/searchers/advanced/rpc-endpoint#flashbots_getuserstats
        return res["result"]


class FlashbotBundleOps:
    """Ongoing"""

    def __init__(self, w3: Web3, bundle_hash: str, target_block: int, tx: List[str]):
        self.w3 = w3
        self.target_block = target_block
        self.bundle_hash = bundle_hash
        self.tx = tx

    def wait(self):
        """Waits until the target block has been reached"""
        while self.w3.eth.block_number < self.target_block:
            time.sleep(1)

    def receipts(self) -> List:
        """
        Returns all the transaction receipts from the submitted bundle
        https://web3py.readthedocs.io/en/stable/web3.eth.html?highlight=get_transaction_receipt#web3.eth.Eth.get_transaction_receipt
        """
        self.wait()
        return list(
            map(
                lambda tx: self.w3.eth.get_transaction_receipt(self.w3.keccak(tx)),
                self.tx,
            )
        )

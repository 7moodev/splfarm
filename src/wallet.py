import os
from solders import message
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
import base58
import pandas as pd
import numpy as np
import json
import utils

class Wallet:
    url = os.environ.get("solrpc")
    jup_url = "https://quote-api.jup.ag/v6"
    shared_transaction_log = pd.DataFrame(columns=['wallet', 'type', 'from', 'to', 'amount', 'slippage', 'date', 'hash'])
    shared_vol = 0
    def __init__(self, which_wallet: int=0):        
        self.volume_sol = 0
        self.volume_usd = 0
        self.client = AsyncClient(Wallet.url)
        self.private_key = os.environ.get(f"spl{which_wallet}")
        if not self.private_key:
            raise Exception(f"Environment variable spl{which_wallet} not set.")
        self.keypair = Keypair.from_bytes(base58.b58decode(self.private_key))
        self.address = self.keypair.pubkey()
        self.volume = 0

    def get_balance(self, token_address=None):
        if token_address is None:
            return utils.get_solana_balance(str(self.address))
        else:
            return utils.get_token_balance(str(self.address), token_address)
    def get_qoute_on_jupiter(self, input: str, output: str, amount: int, slippage=0.5, 
                             exactIn=True, include_dexes=[],
                             onlyDirectRoutes=False):
        qoute, out_amount, price_impact, slippage, in_amount_usd, out_amount_usd, delta_in_out_usd =utils.get_quote(input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes)
        return qoute, out_amount, price_impact, slice, in_amount_usd, out_amount_usd, delta_in_out_usd
    

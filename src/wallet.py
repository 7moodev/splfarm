import os
from solders import message
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
import base58
import utils #where most functions are implemented
import json

class Wallet:
    url = os.environ.get("solrpc")
    jup_url = "https://quote-api.jup.ag/v6"
    def __init__(self, which_wallet: int=0):    
        self.which_wallet = which_wallet    
        self.client = AsyncClient(Wallet.url)
        self.private_key = os.environ.get(f"spl{which_wallet}")
        if not self.private_key:
            raise Exception(f"Environment variable spl{which_wallet} not set.")
        self.keypair = Keypair.from_bytes(base58.b58decode(self.private_key))
        self.address = self.keypair.pubkey()
        self.volume = 0
        self.swaps = 0
        with open('../constants.json', 'r') as file:
            self.tokens = (json.load(file)["tokens"])
    def get_balance(self, ticker=None):
        if ticker is None:
            return utils.get_balance(str(self.address))
        else:
            return utils.get_balance(str(self.address), self.tokens[ticker])
    def get_qoute_on_jupiter(self, input: str, output: str, amount: int, slippage=0.5, 
                             exactIn=True, include_dexes=[],
                             onlyDirectRoutes=False):
        qoute, out_amount, price_impact, slippage, in_amount_usd, out_amount_usd, delta_in_out_usd =utils.get_quote(self.tokens[input], self.tokens[output], amount, slippage, exactIn, include_dexes, onlyDirectRoutes)
        return qoute, out_amount, price_impact, slice, in_amount_usd, out_amount_usd, delta_in_out_usd
    def swap_on_jupiter(self, input: str, output: str, amount: int=None, slippage=0.5, 
                             exactIn=True, include_dexes=[],
                             onlyDirectRoutes=False):
        link, in_amount_usd,*_ =utils.swap(self.keypair, self.tokens[input], self.tokens[output], amount, slippage, exactIn, include_dexes, onlyDirectRoutes)
        self.volume += in_amount_usd
        self.swaps += 1
        
    

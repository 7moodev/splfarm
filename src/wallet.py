import os
from solders.pubkey import Pubkey
from solana.rpc.types import TxOpts
import base58
from solders.keypair import Keypair
from utils import Utils #where most functions are implemented
import json

class Wallet:
    url = os.environ.get("solrpc")
    jup_url = "https://quote-api.jup.ag/v6"
    def __init__(self, which_wallet: int=0):    
        self.which_wallet = which_wallet    
        self.private_key = os.environ.get(f"spl{which_wallet}")
        if not self.private_key:
            raise Exception(f"Environment variable spl{which_wallet} not set.")
        self.keypair = Keypair.from_bytes(base58.b58decode(self.private_key))
        self.address = self.keypair.pubkey()
        self.volume = 0
        self.swaps = 0
        self.open_limits = 0
        self.utils = Utils()
        with open('../constants.json', 'r') as file:
            self.tokens = (json.load(file)["tokens"])
    def get_balance(self, address=None):
        if address is None:
            return self.utils.get_balance(str(self.address))
        else:
            return self.utils.get_balance(str(self.address), address)
    def get_qoute_on_jupiter(self, input: str, output: str, amount: int, slippage=0.5, 
                             exactIn=True, include_dexes=[],
                             onlyDirectRoutes=False):
        qoute, out_amount, price_impact, slippage, in_amount_usd, out_amount_usd, delta_in_out_usd =self.utils.get_quote(input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes)
        return qoute, out_amount, price_impact, slice, in_amount_usd, out_amount_usd, delta_in_out_usd
    def swap_on_jupiter(self, input: str, output: str, amount: int=None, slippage=1, 
                             exactIn=True, include_dexes=[],
                             onlyDirectRoutes=False):
        link, in_amount_usd,*_ =self.utils.swap_on_jupiter(self.keypair, input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes)
        self.volume += in_amount_usd
        self.swaps += 1
    def swap_on_jupiter_safe(self, input: str, output: str, amount: int=None, slippage=1,
                             exactIn=True, include_dexes=[],
                             onlyDirectRoutes=False):
        link, in_amount_usd,*_ =self.utils.swap_on_jupiter(self.keypair, input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes, True)
        self.volume += in_amount_usd
        self.swaps += 1
    def get_simple_quote(self, input: str, output: str, amount: int):
        return self.utils.get_simple_quote(input, output, amount)
        
    def get_all_balances(self):
        
        total = self.get_balance()
        tokens = list(self.tokens) 
        tokens.pop(0)   
        for token in tokens:
                token = token["address"]
                if self.get_balance(token) > 0:
                    total += self.utils.get_simple_quote(token, self.tokens[0]["address"], self.get_balance(token))
                else:
                    continue
        return total
    def limit_on_jupiter(self, input:str, output:str, price:float, amount:int, expireAt = None):
        link, value_usd = self.utils.limit_on_jupiter(self.keypair, self.tokens[input], self.tokens[output], price, amount, expireAt)
        self.volume += value_usd
        self.open_limits +=1
        

    ## to do's:
    # 1. get_all_balances
    # fix erorrs, and integrate all balances to main.py for ease of use
    
    


import os
import requests
import json
from solders import message
from blessings import Terminal
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.transaction import VersionedTransaction
from solana.rpc.commitment import Processed, Finalized, Confirmed
import base58
import base64
from solana.rpc.types import TxOpts


t = Terminal()
solana_url = os.environ.get("solrpc")
def get_balance(wallet_address, token_address=None):
    headers = {
        "Content-Type": "application/json"
    }
    # If no token_address is provided, get the SOL balance
    if token_address is None:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_address]
        }
        response = requests.post(solana_url, json=payload, headers=headers)
        if response.status_code == 200:
            balance_data = response.json()
            if "result" in balance_data:
                lamports = balance_data["result"]["value"]
                sol_balance = lamports / 1_000_000_000  # Convert lamports to SOL
                return  sol_balance
            else:
                raise ValueError("Invalid response from the Solana API.")
        else:
            raise ConnectionError(f"Failed to connect to Solana API. Status code: {response.status_code}")

    # If a token_address is provided, get the token balance
    else:
        # Fetch the token balance for the specified token address and wallet
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet_address,
                {"mint": token_address},
                {"encoding": "jsonParsed"}
            ]
        }
        response = requests.post(solana_url, json=payload, headers=headers)
        if response.status_code == 200:
            accounts_data = response.json()
            if "result" in accounts_data and "value" in accounts_data["result"]:
                token_balance = 0
                for account in accounts_data["result"]["value"]:
                    token_balance += int(account["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])

                # Fetch the token decimals
                decimals = get_token_decimals(token_address)
                token_balance /= 10 ** decimals
                return token_balance
            else:
                raise ValueError("Invalid response from the Solana API.")
        else:
            raise ConnectionError(f"Failed to connect to Solana API. Status code: {response.status_code}")

def get_token_decimals(mint_address):
    # Helper function to fetch token decimals
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenSupply",
        "params": [mint_address]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(solana_url, json=payload, headers=headers)
    if response.status_code == 200:
        supply_data = response.json()
        if "result" in supply_data and "value" in supply_data["result"]:
            decimals = supply_data["result"]["value"]["decimals"]
            return decimals
        else:
            raise ValueError("Invalid response from the Solana API.")
    else:
        raise ConnectionError(f"Failed to connect to Solana API. Status code: {response.status_code}")
def find_ticker(address):
    """
    A local reverse function to return a ticker by passing it's Token address
    """
    with open('constants.json', 'r') as file:
        config_data = (json.load(file)["tokens"])
    for ticker, token_address in config_data.items():
        if token_address == address:
            return ticker
    return None

def get_quote(input:str, output:str, amount:int, slippage:float=0.5,
            exactIn:bool=True, include_dexes:list=[],
            onlyDirectRoutes:bool=False):
    print(t.yellow("Fetching Qoute..."))
    """
        Performs a quote request to the Jup API.

        Args:
            inputMint (str): The input token mint address.
            outputMint (str): The output token mint address.
            amount (int): The amount of input tokens.
            slippageBps (Optional[int]): BPS slippage percentage.
            exactIn (bool): Swap mode (ExactIn or ExactOut).
            platformFeeBps (Optional[int]): Platform fee in BPS.
            onlyDirectRoutes (Optional[bool]): Whether to limit to direct routes.
            asLegacyTransaction (Optional[bool]): Whether to use legacy transaction.
            excludeDexes (Optional[list]): List of DEXes to exclude.
            maxAccounts (Optional[int]): Maximum number of accounts involved in routing.

        Returns:
            Result: A Result object with quote response data or error details.
                The data returned on success will be a dictionary with keys:
                - inputMint: Input token mint address.
                - inAmount: Amount of input tokens.
                - outputMint: Output token mint address.
                - outAmount: Amount of output tokens.
                - otherAmountThreshold: Threshold amount for other tokens.
                - swapMode: Swap mode used (ExactIn or ExactOut).
                - slippageBps: BPS slippage percentage.
                - platformFee: Platform fee information.
                - priceImpactPct: Price impact percentage.
                - routePlan: List of route plans with swap information.
                - contextSlot: Context slot information.
                - timeTaken: Time taken for the operation.
                Example:
                {
                    'inputMint': 'So11111111111111111111111111111111111111112',
                    'inAmount': '1000000',
                    'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
                    'outAmount': '148206',
                    'otherAmountThreshold': '148192',
                    'swapMode': 'ExactIn',
                    'slippageBps': 1,
                    'platformFee': None,
                    'priceImpactPct': '0',
                    'routePlan': [
                        {
                            'swapInfo': {
                                'ammKey': 'DJFoQN5yNVtoEhoXiKqmYFXowQcPJSvB3BAavEcdEi7s',
                                'label': 'Meteora DLMM',
                                'inputMint': 'So11111111111111111111111111111111111111112',
                                'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
                                'inAmount': '1000000',
                                'outAmount': '148206',
                                'feeAmount': '104',
                                'feeMint': 'So11111111111111111111111111111111111111112'
                            },
                            'percent': 100
                        }
                    ],
                    'contextSlot': 275023015,
                    'timeTaken': 0.031721628
                }
        """
 
    def _get_quote_simple(input:str, output:str, amount):

        amount = int(amount * (10**get_token_decimals(input)))
        url = f"https://quote-api.jup.ag/v6/quote?inputMint={input}&outputMint={output}&amount={amount}"
        payload = {}
        headers = {
        'Accept': 'application/json'
        }
        
    # print(f"fetching for: {input}, and for {output}, and for {amount}")
        response = requests.get(url, headers=headers, data=payload)
        if response.status_code == 200:
                # Parse the JSON directly from the response object
                data = response.json()
                # Extracting key values
                out_amount = int(data["outAmount"])/10**get_token_decimals(output)
                return out_amount
        else:
            raise ConnectionError(f"Failed to connect to Jupiter API. Status code: {response.status_code}")

    slippage = int(slippage * 100)
    in_amount_usd = (amount if input == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" else _get_quote_simple(
        input,"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",amount)
    )
    amount = int(amount * (10**get_token_decimals(input)))
    exactIn = "ExactIn" if exactIn else"ExactOut"
    url = f"https://quote-api.jup.ag/v6/quote?inputMint={input}&outputMint={output}&amount={amount}&swapMode={exactIn}&onlyDirectRoutes{onlyDirectRoutes}"
    payload = {}
    headers = {
    'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, data=payload)
    if response.status_code == 200:
            qoute = response.json()
            out_amount = int(qoute["outAmount"])/10**get_token_decimals(output)
            out_amount_usd = out_amount if output == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" else _get_quote_simple (output, "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", int(out_amount))
            delta_in_out_usd = in_amount_usd - out_amount
            price_impact = qoute["priceImpactPct"]
            return qoute, out_amount, price_impact, slippage, in_amount_usd, out_amount_usd, delta_in_out_usd
    else:
        raise ConnectionError(f"Failed to connect to Jupiter API. Status code: {response.status_code}")
def swap(keypair: Keypair, input:str, output:str, amount:int,
          slippage:int=0.5, exactIn:bool=True,
            include_dexes:list=[], onlyDirectRoutes:bool=False):
    url = "https://quote-api.jup.ag/v6/swap"
    client = Client(solana_url)
    pubkey = str(keypair.pubkey())
    qoute, *_ = get_quote(input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes)
    payload = {              
                                    "userPublicKey": pubkey,
                                    "quoteResponse": qoute,
                                    "wrapAndUnwrapSol": True,
                                    "useSharedAccounts": True,
                                    "feeAccount": None,
                                    "trackingAccount": None,
                                    "computeUnitPriceMicroLamports": None,
                                    "asLegacyTransaction": False,
                                    "useTokenLedger": False,
                                    "destinationTokenAccount": None,
                                   }
    response = requests.post(url, json=payload)
    print(t.yellow("Preparing Transaction..."))
    if response.ok:
        tx = response.json()["swapTransaction"]
        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(tx))
        signature = keypair.sign_message(message.to_bytes_versioned(raw_transaction.message))
        signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
        result = client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        transaction_id = json.loads(result.to_json())['result']
        link = f"https://solscan.io/tx/{transaction_id}"
        print(t.green("Swapped "), end="")
        print(t.green(f"{t.bold(str(amount))} {find_ticker(input)} for {find_ticker(output)}"))
        print(t.blue(f"Explorer: {link}"))
        return link
    else:
        print("Failed returning a transaction object")





   







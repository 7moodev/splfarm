
import os
import requests
import json
from blessings import Terminal
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.transaction import VersionedTransaction
from solana.rpc.commitment import Processed, Finalized, Confirmed
from solana.transaction import Transaction
#import solders.compute_budget
import base58
import base64
from solana.rpc.types import TxOpts
from log import log_tx, log_qt, log_fl #used for logging and storing transaction history
import json

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
        response = requests.post("https://api.mainnet-beta.solana.com", json=payload, headers=headers)
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
                token_balance /= float(10 ** decimals)
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
    response = requests.post("https://api.mainnet-beta.solana.com", json=payload, headers=headers)
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
    with open('../constants.json', 'r') as file:
        config_data = (json.load(file)["tokens"])
    for ticker, token_address in config_data.items():
        if token_address == address:
            return ticker
    return None
def _get_quote_simple(input:str, output:str, amount):
        amount = int(amount * (10**get_token_decimals(input)))
        url = f"https://quote-api.jup.ag/v6/quote?inputMint={input}&outputMint={output}&amount={amount}"
        payload = {}
        headers = {
        'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers, data=payload)
        if response.status_code == 200:
                # Parse the JSON directly from the response object
                data = response.json()
                # Extracting key values
                out_amount = int(data["outAmount"])/10**get_token_decimals(output)
                return out_amount
        else:
            raise ConnectionError(f"Failed to connect to Jupiter API. Status code: {response.status_code}")
def get_quote(input:str, output:str, amount:float, slippage:float=0.5,
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

    slippage = int(slippage * 100)
    in_amount_usd = (amount if input == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" else _get_quote_simple(
        input,"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",amount)
    )
    amount = int(amount * (10**get_token_decimals(input)))
    exactIn = "ExactIn" if exactIn else"ExactOut"
    url = f"https://quote-api.jup.ag/v6/quote?inputMint={input}&outputMint={output}&amount={amount}&swapMode={exactIn}&onlyDirectRoutes{onlyDirectRoutes}&asLegacyTransaction=true&slippageBps={slippage}"
    payload = {}
    headers = {
    'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers, data=payload)
    if response.status_code == 200:
            qoute = response.json()
            out_amount = int(qoute["outAmount"])/10**get_token_decimals(output)
            out_amount_usd = out_amount if output == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" else _get_quote_simple (output, "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", (out_amount))
            delta_in_out_usd = in_amount_usd - out_amount
            price_impact = qoute["priceImpactPct"]
            log_qt(qoute)
            return qoute, out_amount, price_impact, slippage, in_amount_usd, out_amount_usd, delta_in_out_usd
    else:
        raise ConnectionError(f"Failed to connect to Jupiter API. Status code: {response.status_code}")
def swap(keypair: Keypair, input:str, output:str, amount:float=None,
          slippage:int=0.5, exactIn:bool=True,
            include_dexes:list=[], onlyDirectRoutes:bool=False, max_tries: int=1):
    
    if input == output:
        raise ValueError(t.red(t.bold("Input and output tokens must be different.")))
    if amount is None:
        if input == "So11111111111111111111111111111111111111112":
            amount = get_balance(str(keypair.pubkey())) - 0.0025
        amount = get_balance(str(keypair.pubkey()), input)
    else:
        if (amount * 10**get_token_decimals(input)) < 30:
            raise ValueError(t.red(t.bold("Amount is too small.")))
        if input == "So11111111111111111111111111111111111111112":
            if amount <= 0:
                raise ValueError(t.red(t.bold("Amount must be greater than zero.")))
            elif amount > get_balance(str(keypair.pubkey())) - 0.0025:
                raise ValueError(t.bold(t.red("Insufficient balance to perform the swap.")))
        else:
            if amount <= 0:
                raise ValueError(t.red(t.bold("Amount must be greater than zero.")))
            elif get_balance(str(keypair.pubkey())) < 0.001:
                raise ValueError(t.bold(t.red("No Gas fees available to perform the swap.")))
            elif amount> get_balance(str(keypair.pubkey()), input):
                raise ValueError(t.bold(t.red("Insufficient balance to perform the swap.")))
    
    url = "https://quote-api.jup.ag/v6/swap"
    client = Client(solana_url)
    pubkey = str(keypair.pubkey())
    qoute, out_amount, _, _, in_amount_usd, out_amount_usd, *_ = get_quote(input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes)
    payload = {              
                                    "userPublicKey": pubkey,
                                    "quoteResponse": qoute,
                                    "wrapAndUnwrapSol": True,
                                    "useSharedAccounts": True,
                                    "feeAccount": None,
                                    "trackingAccount": None,
                                    "computeUnitPriceMicroLamports": None,
                                    "asLegacyTransaction": True,
                                    "useTokenLedger": False,
                                    "destinationTokenAccount": None,
                                    "dynamicComputeUnitLimit": True,
                                   }
    #we'll consider the fees paid
    feeMint = qoute["routePlan"][0]["swapInfo"]["feeMint"]
    feeUSDC = 0
    feesSOL = 0
    feeAmount = float(qoute["routePlan"][0]["swapInfo"]["feeAmount"])
    if feeAmount > 25:
        feeAmount = float(float(qoute["routePlan"][0]["swapInfo"]["feeAmount"]) / 10**get_token_decimals(feeMint))
        if feeMint == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":
            feesUSDC = feeAmount
            feesSOL = _get_quote_simple(feeMint, "So11111111111111111111111111111111111111112", feeAmount)
        elif feeMint == "So11111111111111111111111111111111111111112":
            feeUSDC = _get_quote_simple(feeMint, "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", feeAmount)
            feesSOL = feeAmount
        else:
            feesUSDC = _get_quote_simple(feeMint, "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", feeAmount)
            feesSOL = _get_quote_simple(feeMint, "So11111111111111111111111111111111111111112", feeAmount)
    response = requests.post(url, json=payload)
    print(t.yellow("Preparing Transaction..."))
    if response.ok:
        json_tx = response.json()["swapTransaction"]
        tx = Transaction.deserialize(base64.b64decode(json_tx))
        fee_lamports = client.get_fee_for_message(tx.compile_message()).value / 10**9
        compUnitLimit = response.json()["computeUnitLimit"] 
        prioLamports = response.json()["prioritizationType"]["computeBudget"]["microLamports"] / 10**6
        prio_fee = (compUnitLimit * prioLamports) / 10**9
        chain_fee = fee_lamports+prio_fee
        feesSOL += chain_fee
        opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        try: 
            result =client.send_transaction(tx, keypair, opts=opts, recent_blockhash=client.get_latest_blockhash().value.blockhash)
        except Exception as e:
            log_fl(str(e))
            print(t.bold(t.red(f"Transaction Failed")))
            print(t.cyan("Trying again..."))
            if max_tries > 0:
                swap(keypair, input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes, max_tries-1)
            else:
                print(t.bold(t.red("Max tries reached. Transaction failed")))
                return
            return
        feeUSDC+=(_get_quote_simple(tokens["SOL"], tokens["USDC"], chain_fee))
        transaction_id = json.loads(result.to_json())['result']
        link = f"https://solscan.io/tx/{transaction_id}"
        print(t.green("Swapped "), end="")
        print(t.green(f"{t.bold(str(amount))} {t.bold(find_ticker(input))} for {t.green(t.bold(str(format(float(out_amount), '.12f'))))} {t.bold(find_ticker(output))}"), end = "")
        print(t.magenta((f" and paid ${str(feeUSDC)} in fees")))
        print(t.blue(f"Explorer: {link}"))
        print(t.bold(t.white("==============================================")))
        log_tx(pubkey, find_ticker(input), find_ticker(output), amount, out_amount, feeUSDC, feesSOL, slippage, in_amount_usd, link)
        return link, in_amount_usd, out_amount_usd
    else:
        log_fl(response.json())
        print(t.bold(t.red("Transaction Failed")))
        print(t.cyan("Trying again..."))
        if max_tries > 0:
            swap(keypair, input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes, max_tries-1)
        else:
            print(t.bold(t.red("Max tries reached. Transaction failed")))
            return
# def swap_on_raydium(keypair:Keypair ,input: str, output: str, amount: int, slippage_bps: int):


#         private_key = keypair

#         amount = int(amount * 10**get_token_decimals(input))

#         # Placeholder for Raydium API URL and transaction construction
#         raydium_api_url = " https://api-v3.raydium.io/"
        
#         # Construct the transaction payload (example structure, adjust as needed)
#         payload = {
#             "inputMint": input,
#             "outputMint": output,
#             "amount": amount,
#             "slippage": slippage_bps / 100,
#             "wallet": str(private_key.pubkey())
#         }

#         # Send the swap request to Raydium
#         response = requests.post(raydium_api_url, json=payload)
#         print(response)
#         print(response.json())
#         response.raise_for_status()
#         transaction_data = response.json()['data']

if __name__ == "__main__":
    with open('../constants.json', 'r') as file:
        tokens = (json.load(file)["tokens"])
    private_key = os.environ.get(f"spl{0}")
    if not private_key:
            raise Exception(f"Environment variable spl{0} not set.")
    keypair = Keypair.from_bytes(base58.b58decode(private_key))
    swap(keypair, tokens["USDC"], tokens["SOL"], 4)







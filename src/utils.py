
import os
import requests
import json
from blessings import Terminal
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.transaction import VersionedTransaction
from solana.rpc.commitment import Processed, Finalized, Confirmed
from solana.transaction import Transaction
import traceback
#import solders.compute_budget
import base58
import base64
from solana.rpc.types import TxOpts
from log import log_tx, log_qt, log_fl, log_lim #used for logging and storing transaction history
import json

"""
Conventions: 
-Input and outputs refer to token addresses and are passed as a whole in string format (not the ticker!).
-Amounts are passes as they are known to front end users, i.e 1 SOL or 0.5 SOL, not in Lamports!
-Funtions that are able to perform trades, like swaps and limits, expect a keypair argument.
-
"""
class Utils():
    t = Terminal()
    with open('../constants.json', 'r') as file:
            constants = (json.load(file))
            dexes = constants["dexes"]
            tokens = constants["tokens"]
    custom_rpc = os.environ.get("solrpc")
    if custom_rpc is None:
        print(t.red("Using Solana's default RPC. Please set your custom one as an environment variable \"solrpc\" "))
        custom_rpc = "https://api.devnet.solana.com"
    mainnet_rpc = "https://api.mainnet-beta.solana.com"
    jup_url =  "https://quote-api.jup.ag/v6/"
    usdc_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    sol_address = "So11111111111111111111111111111111111111112"
    def __init__(self) -> None:
        pass
    def get_priority_fee_jup(priority:int = 1):
        prio = "25" if priority==1 else "50" if priority==2 else "75" if priority==3 else "15"
        payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "qn_estimatePriorityFees",
        "params": {
            "last_n_blocks": 100,
            "account": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
        }
        })
        headers = {
        'Content-Type': 'application/json',
        'x-qn-api-version': '1'
        }
        response = requests.request("POST", Utils.custom_rpc, headers=headers, data=payload)
        return response.json()["result"]["per_compute_unit"]["percentiles"][prio]

    def get_balance(self,wallet_address, token_address=None):
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
            response = requests.post(Utils.custom_rpc, json=payload, headers=headers)
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
            response = requests.post(Utils.custom_rpc, json=payload, headers=headers)
            if response.status_code == 200:
                accounts_data = response.json()
                if "result" in accounts_data and "value" in accounts_data["result"]:
                    token_balance = 0
                    for account in accounts_data["result"]["value"]:
                        token_balance += int(account["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])

                    # Fetch the token decimals
                    decimals = self.get_token_decimals(token_address)
                    token_balance /= float(10 ** decimals)
                    return token_balance
                else:
                    raise ValueError("Invalid response from the Solana API.")
            else:
                raise ConnectionError(f"Failed to connect to Solana API. Status code: {response.status_code}")
    def get_token_decimals(self,mint_address):
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
        response = requests.post(Utils.custom_rpc, json=payload, headers=headers)
        if response.status_code == 200:
            supply_data = response.json()
            if "result" in supply_data and "value" in supply_data["result"]:
                decimals = supply_data["result"]["value"]["decimals"]
                return decimals
            else:
                raise ValueError("Invalid response from the Solana API.")
        else:
            raise ConnectionError(f"Failed to connect to Solana API. Status code: {response.status_code}")
    def find_token_data_by_address(self, address=None, ticker=None ):
        if len(address) <= 7:
            ticker = address
            address = None
        """
        Finds token data by address or ticker.
        Input: address or ticker
        Output: ticker, decimals, slippage (if address is provided)
        Output: address, decimals, slippage (if ticker is provided)
        """
        if address is None and ticker is not None:
            for token in Utils.tokens:
                if token["ticker"] == ticker:
                    return token["address"], token["decimals"], token["slippage"]
        # Loop through each token in the JSON file
        elif address is not None and ticker is None:
            for token in Utils.tokens:
                if token["address"] == address:
                    return token["ticker"], token["decimals"], token["slippage"]
        elif address is not None and ticker is not None:
            print(Utils.t.red("Please provide either token ticker or token address!"))
            return None
        else:
            return None 
    def get_simple_quote(self,input:str, output:str, amount):
            jup_url = Utils.jup_url + "quote"
            amount = int(amount * (10**self.get_token_decimals(input)))
            jup_url = f"{jup_url}?inputMint={input}&outputMint={output}&amount={amount}"
            payload = {}
            headers = {
            'Accept': 'application/json'
            }

            response = requests.get(jup_url, headers=headers, data=payload)
            if response.status_code == 200:
                    # Parse the JSON directly from the response object
                    data = response.json()
                    # Extracting key values
                    out_amount = int(data["outAmount"])/10**self.get_token_decimals(output)
                    return out_amount
            else:
                raise ConnectionError(f"Failed to connect to Jupiter API. Status code: {response.status_code}")
    def get_quote(self,input:str, output:str, amount:float, slippage:float=0.5,
                exactIn:bool=True, include_dexes:list=[],
                onlyDirectRoutes:bool=False, input_ticker:str=None, output_ticker:str=None, input_decimals:int=None, output_decimals:int=None
            ):
        jup_url = Utils.jup_url + "quote"
        print(Utils.t.yellow("Fetching Qoute..."))
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
        if input_ticker is None or output_ticker is None or input_decimals is None or output_decimals is None:
            input_ticker, input_decimals, input_slippage = self.find_token_data_by_address(input)
            output_ticker, output_decimals, output_slippage = self.find_token_data_by_address(output)
            slippage = max(input_slippage, output_slippage)
        slippage = int(slippage * 100)
        in_amount_usd = (amount if input == Utils.usdc_address else self.get_simple_quote(
            input,Utils.usdc_address,amount)
        )
        amount = int(amount * (10**input_decimals))
        exactIn = "ExactIn" if exactIn else"ExactOut"
    
        jup_url = f"{jup_url}?inputMint={input}&outputMint={output}&amount={amount}&swapMode={exactIn}&onlyDirectRoutes{onlyDirectRoutes}&asLegacyTransaction=true&slippageBps={slippage}"
        payload = {}
        headers = {
        'Accept': 'application/json'
        }
 
        response = requests.get(jup_url, headers=headers, data=payload)
        if response.status_code == 200:
                qoute = response.json()
                out_amount = int(qoute["outAmount"])/10**output_decimals
                out_amount_usd = out_amount if output == Utils.usdc_address else self.get_simple_quote (output, Utils.usdc_address, (out_amount))
                delta_in_out_usd = in_amount_usd - out_amount
                price_impact = qoute["priceImpactPct"]
                log_qt(qoute)
                return qoute, out_amount, price_impact, slippage, in_amount_usd, out_amount_usd, delta_in_out_usd
        else:
            raise ConnectionError(f"Failed to connect to Jupiter API. Status code: {response.status_code}")
    def swap_on_jupiter(self,keypair: Keypair, input:str, output:str, amount:float=None,
            slippage:int=None, exactIn:bool=True,
                include_dexes:list=[], onlyDirectRoutes:bool=False, max_tries: int=1, priority:bool = False):
        jup_url = Utils.jup_url +"swap"
        input_ticker, input_decimals, input_slippage = self.find_token_data_by_address(input)
        output_ticker, output_decimals, output_slippage = self.find_token_data_by_address(output)
        if slippage is None:
            slippage = max(input_slippage, output_slippage)
        else:
            slippage = 0.5
        if input == output:
            raise ValueError(Utils.t.red(Utils.t.bold("Input and output tokens must be different.")))
        if amount is None:
            if input == Utils.sol_address:
                amount = self.get_balance(str(keypair.pubkey())) - 0.0025
            amount = self.get_balance(str(keypair.pubkey()), input)
        else:
            if (amount * 10**input_decimals) < 30:
                raise ValueError(Utils.t.red(Utils.t.bold("Amount is too small.")))
            if input == Utils.sol_address:
                if amount <= 0:
                    raise ValueError(Utils.t.red(Utils.t.bold("Amount must be greater than zero.")))
                elif amount > self.get_balance(str(keypair.pubkey())) - 0.0025:
                    raise ValueError(Utils.t.bold(Utils.t.red("Insufficient SOL balance to perform the swap.")))
            else:
                if amount <= 0:
                    raise ValueError(Utils.t.red(Utils.t.bold("Amount must be greater than zero.")))
                elif self.get_balance(str(keypair.pubkey())) < 0.001:
                    raise ValueError(Utils.t.bold(Utils.t.red("No Gas fees available to perform the swap.")))
                elif amount> self.get_balance(str(keypair.pubkey()), input):
                    raise ValueError(Utils.t.bold(Utils.t.red("Amount exceeds the balance.")))
        

        client = Client(Utils.custom_rpc)
        pubkey = str(keypair.pubkey())
        qoute, out_amount, _, _, in_amount_usd, out_amount_usd, *_ = self.get_quote(input, output, amount, slippage, exactIn, include_dexes,
                                                                                     onlyDirectRoutes, input_ticker, output_ticker, input_decimals,
                                                                                    output_decimals)
        payload = {              
                                        "userPublicKey": pubkey,
                                        "quoteResponse": qoute,
                                        "wrapAndUnwrapSol": True,
                                        "useSharedAccounts": True,
                                        "feeAccount": None,
                                        "trackingAccount": pubkey,
                                        "computeUnitPriceMicroLamports": Utils.get_priority_fee_jup(2) if priority else None,
                                        "asLegacyTransaction": True,
                                        "useTokenLedger": False,
                                        "destinationTokenAccount": None,
                                        "dynamicComputeUnitLimit": False,
                                    }
        #we'll consider the fees paid
        feeMint = qoute["routePlan"][0]["swapInfo"]["feeMint"]
        _, mint_decimals, _ = self.find_token_data_by_address(feeMint)
        mint_decimals = mint_decimals if mint_decimals is not None else self.get_token_decimals(feeMint)
        feeUSDC = 0
        feesSOL = 0
        feeAmount = float(qoute["routePlan"][0]["swapInfo"]["feeAmount"])
        if feeAmount > 25:
            feeAmount = float(float(qoute["routePlan"][0]["swapInfo"]["feeAmount"]) / 10**mint_decimals)
            if feeMint == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":
                feesUSDC = feeAmount
                feesSOL = self.get_simple_quote(feeMint, Utils.sol_address, feeAmount)
            elif feeMint == Utils.sol_address:
                feeUSDC = self.get_simple_quote(feeMint, Utils.usdc_address, feeAmount)
                feesSOL = feeAmount
            else:
                feesUSDC = self.get_simple_quote(feeMint, Utils.usdc_address, feeAmount)
                feesSOL = self.get_simple_quote(feeMint, Utils.sol_address, feeAmount)
                
        response = requests.post(jup_url, json=payload)
        print(Utils.t.yellow("Preparing Transaction..."))
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
                exc = str(e) + "\n" + traceback.format_exc()
                log_fl(str(input + " || "+ output + " || "+ amount +" || "+ response.json()),exc)
                print(Utils.t.bold(Utils.t.red(f"Transaction Failed")))
                print(Utils.t.cyan("Trying again..."))
                if max_tries > 0:
                    self.swap_on_jupiter(keypair, input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes, max_tries-1)
                else:
                    print(Utils.t.bold(Utils.t.red("Max tries reached. Transaction failed")))
                    return
                return

            feeUSDC += (self.get_simple_quote(Utils.sol_address, Utils.usdc_address, chain_fee))
            transaction_id = json.loads(result.to_json())['result']
            link = f"https://solscan.io/tx/{transaction_id}"
            print(Utils.t.green("Swapped "), end="")
            print(Utils.t.green(f"{Utils.t.bold(str(amount))} {Utils.t.bold(input_ticker)} for {Utils.t.green(Utils.t.bold(str(format(float(out_amount), '.12f'))))} {Utils.t.bold(output_ticker)}"), end = "")
            print(Utils.t.magenta((f" and paid ${str(feeUSDC)} in fees")))
            print(Utils.t.blue(f"Explorer: {link}"))
            print(Utils.t.bold(Utils.t.white("==============================================")))
            log_tx(pubkey, input_ticker, output_ticker, amount, out_amount, feeUSDC, feesSOL, slippage, in_amount_usd, link)
            return link, in_amount_usd, out_amount_usd
        else:
            exc = str(response.json()) + "\n" + traceback.format_exc()
            log_fl(str(input + " || "+ output + " || "+ amount +" || "+ response.json()),exc)
            print(Utils.t.bold(Utils.t.red("Transaction Failed")))
            print(Utils.t.cyan("Trying again..."))
            if max_tries > 0:
                self.self.swap_on_jupiter(keypair, input, output, amount, slippage, exactIn, include_dexes, onlyDirectRoutes, max_tries-1)
            else:
                print(Utils.t.bold(Utils.t.red("Max tries reached. Transaction failed")))
                return
            
    def limit_on_jupiter(self,keypair:Keypair, input:str, output: str, price:float, amount:float, expireAt=None):
        jup_url = 'https://jup.ag/api/limit/v1/createOrder'
        input_ticker, input_decimals, input_slippage = self.find_token_data_by_address(input)
        output_ticker, output_decimals, output_slippage = self.find_token_data_by_address(output)
        amount = int(amount * 10**self.get_token_decimals(input))
        out_amount = amount * price 
        headers = {
        'Content-Type': 'application/json'
    }   
        base = Keypair() # made for the order id
        print(Utils.t.yellow("Creating Limit Order..."))
        body = {
        "owner": str(keypair.pubkey()),  # Use wallet's public key as string
        "inAmount": amount,  # e.g., 1000000 represents 1 USDC if inputMint is USDC mint
        "outAmount": out_amount,
        "inputMint": input,  # Input token's mint address as string
        "outputMint": output,  # Output token's mint address as string
        "expiredAt": expireAt,  # Optionally set expiration as Unix timestamp in seconds
        "base": str(base.pubkey())  # Base public key as string
    }
        response = requests.post(jup_url, headers=headers, data=json.dumps(body))
        client = Client(Utils.custom_rpc)
        if response.ok:
            json_tx = response.json()["tx"]
            tx = Transaction.deserialize(base64.b64decode(json_tx))
            fee_lamports = client.get_fee_for_message(tx.compile_message()).value
            feeUSDC=0
    
            if fee_lamports is not None:
                fee = fee_lamports / 10**9
                feeUSDC = self.get_simple_quote(Utils.sol_address,Utils.usdc_address, fee)

            opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
            try: 
                result =client.send_transaction(tx, keypair, base, opts=opts, recent_blockhash=client.get_latest_blockhash().value.blockhash)
            except Exception as e:
                print(Utils.t.bold(Utils.t.red(f"Transaction Failed")))
            transaction_id = json.loads(result.to_json())['result'] 
            amount = amount / 10**self.get_token_decimals(input)
            value = self.get_simple_quote(input, Utils.usdc_address, amount)
            out_amount = out_amount / 10**self.get_token_decimals(output)
            link = f"https://solscan.io/tx/{transaction_id}"
            log_lim(str(keypair.pubkey()), input_ticker, output_ticker, amount, out_amount, feeUSDC, 0, value, link)
            print(Utils.t.green("Created limit order "), end="")
            print(Utils.t.green(f"{Utils.t.bold(str(amount))} {Utils.t.bold(input_ticker)} for {Utils.t.green(Utils.t.bold(str(format(float(out_amount), '.12f'))))} {Utils.t.bold(output_ticker)}"), end = "")
            print(Utils.t.magenta((f" and paid ${str(feeUSDC)} in fees")))
            print(Utils.t.blue(f"Explorer: {link}"))
            print(Utils.t.bold(Utils.t.white("==============================================")))
            return link, value

    # def swap_on_raydium(keypair:Keypair ,input: str, output: str, amount: int, slippage_bps: int):


    #         private_key = keypair

    #         amount = int(amount * 10**self.get_token_decimals(input))

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
    utils = Utils()
    utils.get_priority_fee_jup
    Utils.get_priority_fee_jup()


    # #utils.limit_on_jupiter(keypair, Utils.sol_address, Utils.usdc_address, 141, 0.04)
    # address, decimals, slippage = utils.find_token_data_by_address(ticker="USDC") 
    # address1, decimals1, slippage1 = utils.find_token_data_by_address(ticker="SOL") 
    # print(utils.get_balance(str(keypair.pubkey()), address))
    # utils.swap_on_jupiter(keypair, address, address1, 0.1)
    # utils.swap_on_jupiter(keypair, address, address1, 0.1, priority=True)
  








    ## log limit orders!
    ## log limit orders vols
    ## implement cancel orders with view open orders
    ## less frequent orders but more volume
    ## integrate dca
    ## integrate raydium
    ## see whats up with bridging USDC through arb and portal bridge, maybe consider BASE?
    ## see whats up with Binance withdrawl.
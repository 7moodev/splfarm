
import os
import requests
import pandas as pd
import json
from blessings import Terminal

t = Terminal()
url = os.environ.get("solrpc")


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
        response = requests.post(url, json=payload, headers=headers)
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
        response = requests.post(url, json=payload, headers=headers)
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
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        supply_data = response.json()
        if "result" in supply_data and "value" in supply_data["result"]:
            decimals = supply_data["result"]["value"]["decimals"]
            return decimals
        else:
            raise ValueError("Invalid response from the Solana API.")
    else:
        raise ConnectionError(f"Failed to connect to Solana API. Status code: {response.status_code}")


def get_quote(input, output, amount, slippage = 0.5, exactIn=True, include_dexes=[], onlyDirectRoutes=False):
    USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

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
    in_amount_usd = (amount if input == USDC else _get_quote_simple(
        input,USDC, amount)
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
            # Extracting key values
            out_amount = int(qoute["outAmount"])/10**get_token_decimals(output)
            out_amount_usd = out_amount if output == USDC else _get_quote_simple (output, USDC, int(out_amount))
            delta_in_out_usd = in_amount_usd - out_amount
            price_impact = qoute["priceImpactPct"]
            #print(qoute["routePlan"])
            # print(f"Input Amount: {amount} tokens")
            # print(f"Output Amount: {out_amount} tokens")
            # print(f"Price Impact: {price_impact}%")
            # print(f"In Amount in $: {in_amount_usd}")
            # print(f"Out Amount in $: {out_amount_usd}")
            # print(f"Cooked by slippage $: {delta_in_out_usd}")
            return qoute, out_amount, price_impact, slippage, in_amount_usd, out_amount_usd, delta_in_out_usd
    else:
        raise ConnectionError(f"Failed to connect to Jupiter API. Status code: {response.status_code}")
        
if __name__ == "__main__":
    with open('constants.json', 'r') as file:
        config_data = json.load(file)

        tokens = config_data['tokens']
        dexes = config_data['dexes']     
        # print(t.red('This is red'))
        # print(t.blue('This is bold'))
        
    #print(get_quote(tokens["KIN"],tokens["USDC"], 3000))
    print("")
   



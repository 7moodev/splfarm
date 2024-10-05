import json
import csv
from datetime import datetime, timezone
def log_tx(wallet: str, input_token: str,
                        output_token: str, in_amount: int,
                        out_amount: int, feeUSD: float,
                        feeSOL: float,
                        slippage: float, explorer: str, 
                        json_file='../log/txs.json', csv_file='../log/txs.csv'):
    # Prepare the transaction data
    timestamp = datetime.now(timezone.utc).isoformat()
    transaction = {
       
        "wallet_name": wallet,
        "input": input_token,
        "output": output_token,
        "in": in_amount,
        "out": out_amount,
        "fees $": feeUSD,
        "fees SOL": feeSOL,
        "slippage": slippage,
        "explorer": explorer,
        "timestamp": timestamp,
    }
    # Append to JSON file
    try:
        # Load existing transactions or initialize an empty list
        with open(json_file, 'r') as f:
            transactions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        transactions = []

    # Append new transaction
    transactions.append(transaction)

    # Save the updated transaction log back to JSON
    with open(json_file, 'w') as f:
        json.dump(transactions, f, indent=4)

    # Append to CSV file
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        
        # If the file is empty, write the header first
        if f.tell() == 0:
            writer.writerow(["wallet_name", "input", "output","in", "out", "fees $", "fees SOL", "slippage", "explorer", "timestamp"])
        
        writer.writerow([wallet, input_token, output_token, in_amount, out_amount,feeUSD,feeSOL, slippage, explorer, timestamp])


def log_qt(jupiter_quote: str, json_file='../log/qoutes.json'):
    # Get the current timestamp
    timestamp = datetime.now(timezone.utc).isoformat()
    # Create a dictionary with the timestamp and the raw JSON string
    transaction = {
        "timestamp": timestamp,
        "quote": jupiter_quote  # Save the entire quote string as-is
    }
    # Append to JSON file
    try:
        # Load existing transactions or initialize an empty list
        with open(json_file, 'r') as f:
            transactions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        transactions = []
    # Append new transaction
    transactions.append(transaction)
    # Save the updated transaction log back to JSON
    with open(json_file, 'w') as f:
        json.dump(transactions, f, indent=4)

def log_qt(jupiter_quote: str, json_file='../log/qoutes.json'):
    # Get the current timestamp
    timestamp = datetime.now(timezone.utc).isoformat()
    # Create a dictionary with the timestamp and the raw JSON string
    transaction = {
        "timestamp": timestamp,
        "quote": jupiter_quote  # Save the entire quote string as-is
    }
    # Append to JSON file
    try:
        # Load existing transactions or initialize an empty list
        with open(json_file, 'r') as f:
            transactions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        transactions = []
    # Append new transaction
    transactions.append(transaction)
    # Save the updated transaction log back to JSON
    with open(json_file, 'w') as f:
        json.dump(transactions, f, indent=4)



def log_fl(failed: str, json_file='../log/failed.json'):
    # Get the current timestamp
    timestamp = datetime.now(timezone.utc).isoformat()
    # Create a dictionary with the timestamp and the raw JSON string
    transaction = {
        "timestamp": timestamp,
        "failure": failed  # Save the entire quote string as-is
    }
    # Append to JSON file
    try:
        # Load existing transactions or initialize an empty list
        with open(json_file, 'r') as f:
            transactions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        transactions = []
    # Append new transaction
    transactions.append(transaction)
    # Save the updated transaction log back to JSON
    with open(json_file, 'w') as f:
        json.dump(transactions, f, indent=4)

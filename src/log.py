import json
import csv
from datetime import datetime, timezone
import os
def ensure_log_folder_exists():
    log_dir = os.path.dirname('../log/')
    os.makedirs(log_dir, exist_ok=True)
def log_tx(wallet: str, input_token: str,
                        output_token: str, in_amount: int,
                        out_amount: int, feeUSD: float,
                        feeSOL: float,
                        slippage: float, 
                        valueUSD: int, 
                        explorer: str, 
                        json_file='../log/txs.json', csv_file='../log/txs.csv'):
    ensure_log_folder_exists()
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
        "value $": valueUSD,
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
            writer.writerow(["wallet_name", "input", "output","in", "out", "fees $", "fees SOL", "slippage", "value $","explorer", "timestamp"])
        
        writer.writerow([wallet, input_token, output_token, in_amount, out_amount,feeUSD,feeSOL, slippage,valueUSD, explorer, timestamp])


def log_qt(jupiter_quote: str, json_file='../log/qoutes.json'):
    ensure_log_folder_exists()
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
    ensure_log_folder_exists()
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
    ensure_log_folder_exists()
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
def log_vol(wallet: str, volume: float, csv_file='volume.csv'):
    ensure_log_folder_exists()
    """
    Logs the provided volume for a given wallet into a CSV file.
    Parameters:
        wallet (str): The wallet address.
        volume (float): The volume to log.
        csv_file (str): The path to the CSV file.
    """
    # Get the current timestamp
    timestamp = datetime.now(timezone.utc).isoformat()
    # Prepare the log entry
    log_entry = {
        "last updated": timestamp,
        "wallet": wallet,
        "volume": volume
    }
    
    # Check if the CSV file exists and write the log entry
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as f:
        fieldnames = ['timestamp', 'wallet', 'volume']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write the header only if the file is being created for the first time
        if not file_exists:
            writer.writeheader()
        
        # Write the new log entry
        writer.writerow(log_entry)

def log_rd(starttime:str,swaps:int, volume:float, csv_file='../log/rounds.csv'):
    """
    Logs the number of swaps and total volume for a round into a CSV file.
    Parameters:
        swaps (int): The number of swaps in the round.
        volume (float   
        csv_file (str): The path to the CSV file.
    """
    # Get the current timestamp
    endtime = datetime.now(timezone.utc).isoformat()
    # Prepare the log entry
    log_entry = {
        "start": starttime,
        "end": endtime,
        "swaps": swaps,
        "volume": volume
    }
    # Check if the CSV file exists and write the log entry
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as f:
        fieldnames = ['start','end' ,'swaps', 'volume']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write the header only if the file is being created for the first time
        if not file_exists:
            writer.writeheader()
        
        # Write the new log entry
        writer.writerow(log_entry)
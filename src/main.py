from wallet import Wallet
import time
import os
import json
from blessings import Terminal
from datetime import datetime, timezone
import random
from log import log_rd, log_bal, log_fl
from utils import Utils
t = Terminal()
import traceback
import sys
with open('../constants.json', 'r') as file:
        tokens = (list((json.load(file)["tokens"])))
        tokens.pop(0)

usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
sol = "So11111111111111111111111111111111111111112"
        
rounds = 10 # rounds of swapping all tickers among all wallets once
time_between_rounds = 5*60 # est time to wait between each round, in seconds
time_between_swaps = 60 # est time to wait between each swap, in seconds
time_between_wallets = 10 # est time to wait between each wallet, in seconds
def main():
    """
    A naive farming bot that does random swaps on wallets on verified tickers. It is not inteded to be profitable.

    Implemnted logic consists of wallets, that are created and then passed for swapping in a specified number of rounds.
    In each round, the script iterates through all wallets, perform swaps for all pairs imported from constants.json. Although in this case,
    it would mean that each wallet swaps all tokens before the next wallet starts swapping. Hence there are some cases added 
    that break out of the tokens iteration and move to the next wallet, while also monitoring current wallet's balance and 
    breaking out when it goes below 0.2 SOL.
    
    Amount for each swap from SOL to token X is randomly selected between 25% and 66% of the token balance.
    Amount for each swap from token X to SOL is randomly selected between 50% and 100% of the token balance.
    
    Time between rounds/swaps/wallets is randomly selected between 0 and that value, to prevent it from being a pattern"""
    global rounds
    global time_between_rounds
    print(t.bold(t.blue("========================================== Engine Started ========================================")))
    wallet0 = Wallet(0)
    wallet1 = Wallet(1)
    wallet2 = Wallet(2)
    wallet3 = Wallet(3)
    wallet4 = Wallet(4)
    wallet5 = Wallet(5)
    wallet6 = Wallet(6)
    wallet7 = Wallet(7)
    wallet8 = Wallet(8)
    wallet9 = Wallet(9)
    wallet10 = Wallet(10)
    wallets = [wallet0, wallet1, wallet2, wallet3, wallet4, wallet5, wallet6, wallet7, wallet8, wallet9, wallet10]
    total_vol = 0 #vol in usd
    swaps = 0
    print(t.bold(t.green(f"Total SOL among all wallets: {get_sol_balances(wallets)}")))
    print(t.bold(t.green(f"Total balance among all wallets: {get_all_balances(wallets)}")))
    while True:
        if rounds == 0:
            break
        rounds -= 1
        start = datetime.now(timezone.utc).isoformat()
        print(t.bold(t.red("================== Swapping Started ================")))
        slow_alternating_swaps(wallets)
        for wallet in wallets:
            total_vol +=wallet.volume
            swaps += wallet.swaps 
        log_rd(start,swaps,total_vol)
        print(t.bold(t.green(f"Total volume traded among all wallets: {total_vol}")))
        print(t.bold(t.green(f"Available SOL among all wallets: {get_sol_balances(wallets)}")))
        print(t.bold(t.green(f"Total balance among all wallets: {get_all_balances(wallets)}")))
        print(t.bold(t.red("================== Swapping Ended ==================")))
        time.sleep(random.randint(0,time_between_rounds))
def slow_alternating_swaps(wallets):
        """
        This function will keep swapping on a random wallet at a random time using random tickers and random amounts ranging from
        10% of the wallet balance to 25% of the wallet balance for each swap and up to 90% of wallet utilization for each wallet each round.
        Inputs:
            wallets: list of wallet objects
        Outputs:
            None
        """
        global time_between_swaps
        global time_between_wallets
        random.shuffle(wallets) # for extra randomness
        random_sec = random.randint(0, 59)
        wallets_count = 0
        for wallet in wallets:
            print(t.bold(t.white("Queue entered for ")), end="")
            print(t.bold(t.white(f"Wallet {wallet.which_wallet} (")), end="")
            print(t.bold(t.white(f"{wallets_count}")), end="")
            print(t.bold(t.white("/")), end="")
            print(t.bold(t.white(f"{len(wallets)}")), end="")
            print(t.bold(t.white(")")))
            random.shuffle(tokens)
            sol_balance = wallet.get_balance()
            while True:
                output = (f"{t.black('Planned Second: ')}"
                f"{t.bold(t.black(f'{random_sec}'))} "
                f"{t.black('|| Current Second: ')}"
                f"{t.bold(t.black(f'{datetime.now().second}'))}")
                sys.stdout.write(f'\r{output}\n')
                sys.stdout.flush()
                if datetime.now().second != random_sec:
                    random_sec = random.randint(0,59)
                    if sol_balance<0.2: 
                        print(t.bold(t.white("Wallet balance is below 0.2 SOL. Emptying some tokens:")))
                        for token in tokens:
                            ticker = token['ticker']
                            token = token["address"]
                            
                            token_balance = wallet.get_balance(token)
                            if token_balance != 0:
                                if random_sec %10 == random.randint(0,9):
                                    print(t.bold(t.white("Changing Wallets")))
                                    break # this will ensure that not all tokens have to be processed before the next wallet is processed
                                try: 
                                    print(t.yellow("Swapping "), end ="")
                                    print(t.bold(t.yellow(ticker)), end="")
                                    print(t.yellow(" =======> SOL on wallet "), end="")
                                    print(t.bold(t.yellow(f"{wallet.which_wallet}")))
                                    if wallet.get_simple_quote(token, usdc, token_balance) < 10:
                                        wallet.swap_on_jupiter(token, sol, token_balance)
                                        continue
                                    wallet.swap_on_jupiter(token, sol, random.choice([token_balance, token_balance/2, token_balance/3]), 1)
                                except Exception as e:
                                    exc = str(e) + "\n" + str(traceback.format_exc())
                                    log_fl(token + " || "+ "SOL" + " || "+ str(token_balance) , exc)
                                    print(t.red("Swap Failed"))
                                    continue
                                waiting = random.randint(time_between_swaps/2, time_between_swaps)
                                print(t.black(f"Waiting for {waiting} seconds"))
                                time.sleep(waiting)
                        break
                    else:
                        for token in tokens:
                            sol_balance = wallet.get_balance()
                            ticker = token['ticker']
                            token = token["address"]
                 
                            token_balance = wallet.get_balance(token)
                            if random_sec %10 == random.randint(0,9) or sol_balance<0.2:
                                print(t.bold(t.white("Changing Wallets")))
                                break # this will ensure that not all tokens have to be processed before the next wallet is processed
                            try: 
                                print(t.yellow(f"Swapping SOL =======> "), end="")
                                print(t.bold(t.yellow(ticker)), end="")
                                print(t.yellow(f" on wallet "), end="")
                                print(t.bold(t.yellow(f"{wallet.which_wallet}")))
                                wallet.swap_on_jupiter(sol, token, random.uniform(sol_balance/5, sol_balance/2))
                                
                            except Exception as e:
                                exc = str(e) + "\n" + str(traceback.format_exc())
                                log_fl(token + " || "+ "SOL" + " || "+ str(sol_balance),exc)
                                print(t.red("Swap Failed"))
                                continue
                            waiting = random.randint(time_between_swaps/2, time_between_swaps)
                            print(t.black(f"Waiting for {waiting} seconds"))
                            time.sleep(waiting)
                        break
                waiting = random.randint(1,1)
                print(t.black(f"Waiting for {waiting} seconds"))
                time.sleep(waiting)
            waiting = random.randint(0,time_between_wallets)
            print(t.black(f"Waiting for {waiting} seconds"))
            time.sleep(waiting)
            print(t.magenta("================== Finished swapping for this wallet =================="))

def get_all_balances(wallets):
    total = 0
    listy = []
    for wallet in wallets:
        try:
            balance = wallet.get_all_balances()
            tuple_balance = (wallet.address, balance)
            listy.append(tuple_balance)
            total += balance
        except Exception as e:
            exc = str(e) + "\n" + str(traceback.format_exc())
            log_fl(exc, str(wallet.address))
            print(t.red("Failed to get balance"))
            time.sleep(5)
            continue
    log_bal(datetime.now(timezone.utc).isoformat(), listy, total)
    return total
    
def get_sol_balances(wallets):
    balance = 0
    for wallet in wallets:
        try:
            balance += wallet.get_balance()
        except Exception as e:
            time.sleep(3)
            continue
    return balance
def swap_all_to_sol(wallets):
    for wallet in wallets:
        for token in tokens:
            balance = wallet.get_balance(token)
            if balance != 0:
                try:
                    wallet.swap_on_jupiter(token, "SOL", balance)
                except Exception as e:
                    print(t.red("Swap Failed"))
                    continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(t.bold(t.blue("======================================== Engine Stopped ========================================")))
        sys.exit(0)


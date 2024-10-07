from wallet import Wallet
import time
import os
import json
from blessings import Terminal
from datetime import datetime, timezone
import random
from log import log_rd, log_bal, log_fl
t = Terminal()
import sys
with open('../constants.json', 'r') as file:
        tokens = (list((json.load(file)["tokens"]).keys()))
        tokens.remove("SOL")
        
rounds = 10 # rounds of swapping all tickers among all wallets once
time_between_rounds = 20*60 # est time to wait between each round, in seconds
time_between_swaps = 60*2 # est time to wait between each swap, in seconds
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

    print(t.bold(t.blue("======================================== Engine Started ========================================")))
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
    #print(t.bold(t.green(f"Total balance among all wallets: {get_all_balances(wallets)}")))
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
        for wallet in wallets:
            print(t.bold(t.white("Queue entered for ")), end="")
            print(t.bold(t.white(f"Wallet {wallet.which_wallet}:")))
            random.shuffle(tokens)
            sol_balance = wallet.get_balance()
            while True:
                output = (f"{t.black('Planned Second: ')}"
                f"{t.bold(t.black(f'{random_sec}'))} "
                f"{t.black('|| Current Second: ')}"
                f"{t.bold(t.black(f'{datetime.now().second}'))}")

                    # Print the output and overwrite it on the same line
                sys.stdout.write(f'\r{output}\n')
                sys.stdout.flush()
                if datetime.now().second == random_sec:
                    random_sec = random.randint(0,59)
                    if sol_balance<0.2: 
                        print(t.bold(t.white("Wallet balance is below 0.2 SOL. Emptying some tokens:")))
                        for token in tokens:
                            token_balance = wallet.get_balance(token)
                            if token_balance != 0:
                                if random_sec %10 == random.randint(0,9):
                                    print(t.bold(t.white("Changing Wallets")))
                                    break # this will ensure that not all tokens have to be processed before the next wallet is processed
                                try: 
                                    print(t.yellow("Swapping "), end ="")
                                    print(t.bold(t.yellow(token)), end="")
                                    print(t.yellow(" =======> SOL on wallet "), end="")
                                    print(t.bold(t.yellow(f"{wallet.which_wallet}")))
                                    if token == "MOODENG" or token == "WIF" or token == "POPCAT":
                                         wallet.swap_on_jupiter(token, "SOL", token_balance, slippage=2)
                                    wallet.swap_on_jupiter(token, "SOL", token_balance)
                                except Exception as e:
                                    log_fl(str(e))
                                    print(t.red("Swap Failed"))
                                    continue
                                time.sleep(random.randint(time_between_swaps/2, time_between_swaps))
                        break
                    else:
                        for token in tokens:
                            if random_sec %10 == random.randint(0,9) or wallet.get_balance()<0.2:
                                print(t.bold(t.white("Changing Wallets")))
                                break # this will ensure that not all tokens have to be processed before the next wallet is processed
                            try: 
                                print(t.yellow(f"Swapping SOL =======> "), end="")
                                print(t.bold(t.yellow(token)), end="")
                                print(t.yellow(f" on wallet "), end="")
                                print(t.bold(t.yellow(f"{wallet.which_wallet}")))
                                wallet.swap_on_jupiter("SOL", token, random.uniform(wallet.get_balance()/5, wallet.get_balance()/2))
                                
                            except Exception as e:
                                log_fl(str(e))
                                print(t.red("Swap Failed"))
                                continue
                            time.sleep(random.randint(time_between_swaps/2, time_between_swaps))
                        break
                time.sleep(random.randint(1,1))
            time.sleep(random.randint(0,time_between_wallets))
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






## fix logging of everything
## fix swap failed
#adjust trades size
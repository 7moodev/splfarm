from wallet import Wallet
import time
import os
import json
from blessings import Terminal
from datetime import datetime, timezone
import random
from log import log_rd
t = Terminal()

with open('../constants.json', 'r') as file:
        tokens = (list((json.load(file)["tokens"]).keys()))
        tokens.remove("SOL")
        
rounds = 10 # rounds of swapping all tickers among all wallets once
time_between_rounds = 20*60 # est time to wait between each round, in seconds
time_between_swaps = 60 # est time to wait between each swap, in seconds
time_between_wallets = 60 # est time to wait between each wallet, in seconds
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
    total_vol = 5
    while True:
        if rounds == 0:
            break
        rounds -= 1
        start = datetime.now(timezone.utc).isoformat()
        print(t.bold(t.red("================== Swapping Started ==================")))
       
        print(t.bold(t.black(f"Pre Balances among all wallets: {get_all_balances(wallets)}")))
        slow_alternating_swaps(wallets)
        for wallet in wallets:
              total_vol +=wallet.volume
        swaps = wallet.swaps +5
        log_rd(start,swaps,total_vol)
        print(t.bold(t.green(f"Total volume traded among all wallets: {total_vol}")))
        print(t.bold(t.green(f"Post Balances among all wallets: {get_all_balances(wallets)}")))
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
        random_min = random.randint(0, 59)
        for wallet in wallets:
            print(t.bold(t.white("Queue entered for ")), end="")
            print(t.bold(t.white(f"Wallet {wallet.which_wallet}:")))
            random.shuffle(tokens)
            while True:
                print(t.black("Planned Minute: "), end="")
                print(t.bold(t.black(f"{random_min}")))
                print(t.black("Current Minute: "), end="")
                print(t.bold(t.black(f"{datetime.now().minute}")))
                if wallet.get_balance()<0.2:
                    if datetime.now().minute != random_min:
                        random_min = random.randint(0,59)
                        for token in tokens:
                            token_balance = wallet.get_balance(token)
                            if token_balance != 0:
                                if random_min %10 == random.randint(0,9):
                                    print(t.bold(t.white("Changing Wallets")))
                                    break # this will ensure that not all tokens have to be processed before the next wallet is processed
                                try: 
                                    print(t.yellow("Swapping "), end ="")
                                    print(t.bold(t.yellow(token)), end="")
                                    print(t.yellow(" =======> SOL on wallet "), end="")
                                    print(t.bold(t.yellow(f"{wallet.which_wallet}")))
                                    token_balance = wallet.get_balance(token)
                                    wallet.swap_on_jupiter(token, "SOL", random.uniform(token_balance/2, token_balance))
                                except Exception as e:
                                    print(t.red("Swap Failed"))
                                    continue
                            time.sleep(random.randint(0, time_between_swaps))
                        break
                else:
                    if datetime.now().minute != random_min:
                        random_min = random.randint(0,59)
                        for token in tokens:
                                if random_min %10 == random.randint(0,9) or wallet.get_balance()<0.2:
                                    print(t.bold(t.white("Changing Wallets")))
                                    break # this will ensure that not all tokens have to be processed before the next wallet is processed
                                if wallet.get_balance()< 0.2:
                                    break
                                try: 
                                    print(t.yellow(f"Swapping SOL =======> "), end="")
                                    print(t.bold(t.yellow(token)), end="")
                                    print(t.yellow(f" on wallet "), end="")
                                    print(t.bold(t.yellow(f"{wallet.which_wallet}")))
                                    wallet.swap_on_jupiter("SOL", token, random.uniform(wallet.get_balance()/4, wallet.get_balance()/1.5))
                                except Exception as e:
                                    print(t.red("Swap Failed"))
                                    continue
                                time.sleep(random.randint(0, 59))
                        break
                time.sleep(random.randint(0,time_between_wallets))
            print(t.magenta("================== Finished swapping for this wallet =================="))


def get_all_balances(wallets):
    balance = 0
    for wallet in wallets:
        balance += wallet.get_balance()
    return balance
def swap_all_to_sol(wallets):
    for wallet in wallets:
        for token in tokens:
            try:
                wallet.swap_on_jupiter(token, "USDC", wallet.get_balance(token))
            except Exception as e:
                print(t.red("Swap Failed"))
                continue

if __name__ == "__main__":
     main()
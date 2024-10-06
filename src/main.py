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
        tokens = list((json.load(file)["tokens"]).keys())
        
def main():
    rounds = 10 # each rounds denotes 1 round of swapping all tickers among all wallets once
    print(t.bold(t.blue("======================================== Engine Started ========================================")))
    wallet0 = Wallet(0)
    wallet1 = Wallet(1)
    wallet2 = Wallet(2)
    wallet3 = Wallet(3)
    wallet4 = Wallet(4)
    wallet5 = Wallet(5)
    wallets = [wallet0, wallet1, wallet2, wallet3, wallet4, wallet5]
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
        time.sleep(60*60)
def slow_alternating_swaps(wallets):
        """
        This function will keep swapping on a random wallet at a random time using random tickers and random amounts ranging from
        10% of the wallet balance to 25% of the wallet balance for each swap and up to 90% of wallet utilization for each wallet each round.
        Inputs:
            wallets: list of wallet objects
        Outputs:
            None
        """
        random.shuffle(wallets) # for extra randomness
        random_min = random.randint(0, 59)
        for wallet in wallets:
            print(t.bold(t.white("Queue entered for ")), end="")
            print(t.bold(t.white(f"Wallet {wallet.which_wallet}:")))
            random.shuffle(tokens)
            while True:
                if wallet.get_balance()<0.2:
                    if datetime.now().minute == random_min:
                        random_min = random.randint(0,59)
                        for token in tokens:
                            if random_min %10 == random.randint(0,9):
                                print(t.bold(t.white("Changing Wallets")))
                                break # this will ensure that not all tokens have to be processed before the next wallet is processed
                            try: 
                                wallet.swap_on_jupiter(token, "SOL", random.uniform(wallet.get_balance()/2, wallet.get_balance()))
                                print(t.yellow("Swapping ", end =""))
                                print(t.bold(t.yellow(token)), end="")
                                print(t.yellow(" =======> SOL on wallet "), end="")
                                print(t.bold(t.yellow(f"{wallet.which_wallet}")))
                            except Exception as e:
                                print(t.red("Swap Failed"))
                                continue
                            time.sleep(random.randint(0,60))
                        print("finished swapping for this wallet")
                else:
                        if datetime.now().minute == random_min:
                            random_min = random.randint(0,59)
                            for token in tokens:
                                    if random_min %10 == random.randint(0,9):
                                        print(t.bold(t.white("Changing Wallets")))
                                        break # this will ensure that not all tokens have to be processed before the next wallet is processed
                                    if wallet.get_balance()< 0.2:
                                        break
                                    try: 
                                        wallet.swap_on_jupiter("SOL", token, random.uniform(wallet.get_balance()/3, wallet.get_balance()))
                                        print(t.yellow(f"Swapping SOL =======> "), end="")
                                        print(t.bold(t.yellow(token)), end="")
                                        print(t.yellow(f" on wallet "), end="")
                                        print(t.bold(t.yellow(f"{wallet.which_wallet}")))
                                    except Exception as e:
                                        print(t.red("Swap Failed"))
                                        continue
                                    time.sleep(random.randint(0, 59))
                time.sleep(59)
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
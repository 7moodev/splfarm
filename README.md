
# Solana Farm

**A simple python code to farm Dexes like Jupiter and Raydium for potential airdrops (the former is more likely to be of relevance)**


## Brief Overview:

**wallet**: the wallet class represent a wallet on Solana. It contains attributes that are used for signing transactions like the public key and keypair. Some logging attributes are also there, like trade count and volume \
**utils**: Where most of the heavy work is done. Most used functions are implemented there to reduce code size in other files like wallet.py and main.py \
**main**: here is where the logic of swapping and farming is. There are some pre-implemented routes of farming swaps, however you can use your own for more diversification and sybil avoidance 




## Locally saved invariants

This project assumes that you have some constans in your ~/.zshrc for more secure access of senstive information, like your private keys and rpc urls. You'll then never have to enter these in the code.
 For ease of use and instantiation of Wallet objects, constans shall have the following format


```bash
export solrpc="https://api.mainnet-beta.solana.com”
export spl0="LxPXMnGLsDxR..”
export spl1="VP4es7u5XVDGF1..”
export spl2="2N2yd6eBsl42XS...”
.
.
```
It's advised to obtain a custom rpc url, from services like QuickNode





## Usage/Deployment
With `python 3.9.7` \

run: 
```bash
python3 -m ensurepip --upgrade
```

and after cloning and having `splfarm` as cwd, run:
```bash
pip install -r requirements.txt
```
Head to `main.py`, instantiate desired Wallet objects and adjust desired metrics like logic, size, and trade frequency.
Then run:
```bash
python3 src/main.py
```







## Logging
In `log.py`, processed and failed transactions, fetched qoutes, volume, and swapping rounds are logged to the 'log' folder and are saved in both **json** and **csv**.



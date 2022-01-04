# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os
from constants import *
import bit
from bit.network import NetworkAPI
from web3 import Web3
from web3.middleware import geth_poa_middleware


# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


 
# Create a function called `derive_wallets`
def derive_wallets(coin):
    command = f'php derive -g --mnemonic="{mnemonic}" --cols=path,address,privkey,pubkey --format=json coin={coin}'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

output_eth = derive_wallets(ETH)
output_btctest = derive_wallets(BTCTEST)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = { BTCTEST: output_eth,
          ETH: output_btctest
}

# # Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return w3.eth.account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return bit.PrivateKeyTestnet(priv_key)
        
# # Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == BTCTEST:
        return bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])
    elif coin == ETH:
        return {
                "from": account.address,
                "to": to,
                "value": amount,
                "gasPrice": web3.eth.gasPrice,
                "gas": gasEstimate,
                "nonce": web3.eth.getTransactionCount(account.address),
        }

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    tx = create_tx(coin, account, to, amount)
    signed_tx = account.sign_transaction(tx)
    if coin == ETH:
        return w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    else:
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
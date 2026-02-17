from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

factory_addr = "0xB9fC157394AF804a3578134A6585C0dc9Cc990d4"
crvusd = "0xf939E0A03FB0a03ad1D3da1d3dA1d3dA1d3dA1d3"
usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

abi = [
    {"name": "find_pool_for_coins", "outputs": [{"type": "address"}], "inputs": [{"type": "address", "name": "_from"}, {"type": "address", "name": "_to"}], "stateMutability": "view", "type": "function"},
    {"name": "get_pool_name", "outputs": [{"type": "string"}], "inputs": [{"type": "address", "name": "_pool"}], "stateMutability": "view", "type": "function"},
]

try:
    c = w3.eth.contract(address=w3.to_checksum_address(factory_addr), abi=abi)
    pool = c.functions.find_pool_for_coins(w3.to_checksum_address(crvusd), w3.to_checksum_address(usdc)).call()
    print(f"crvUSD/USDC Pool: {pool}")
    if pool != "0x0000000000000000000000000000000000000000":
         print(f"Name: {c.functions.get_pool_name(pool).call()}")
except Exception as e:
    print(f"Error: {e}")

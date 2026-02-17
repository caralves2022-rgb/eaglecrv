from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

factories = [
    "0xB9fC13c24C528DB8274464f5197012d458b8d9f1",
    "0xB9fC157394AF804a3578134A6585C0dc9Cc990d4",
    "0xF18056BBD320E96A48E3fBF8bC061322531aac99",
    "0x618ad83556565656565656565656565656565656", # Dummy
]

crvusd = "0xf939E0A03FB07F59A73314E73794Be0E57ac1b4E"
usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
usdt = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

abi = [
    {"name": "find_pool_for_coins", "outputs": [{"type": "address"}], "inputs": [{"type": "address"}, {"type": "address"}], "stateMutability": "view", "type": "function"},
    {"name": "get_pool_name", "outputs": [{"type": "string"}], "inputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
]

for f in factories:
    print(f"\nChecking Factory {f}...")
    try:
        c = w3.eth.contract(address=w3.to_checksum_address(f), abi=abi)
        # crvUSD/USDC
        p1 = c.functions.find_pool_for_coins(w3.to_checksum_address(crvusd), w3.to_checksum_address(usdc)).call()
        if p1 != "0x0000000000000000000000000000000000000000":
             print(f"  crvUSD/USDC: {p1}")
        
        # crvUSD/USDT
        p2 = c.functions.find_pool_for_coins(w3.to_checksum_address(crvusd), w3.to_checksum_address(usdt)).call()
        if p2 != "0x0000000000000000000000000000000000000000":
             print(f"  crvUSD/USDT: {p2}")
    except Exception as e:
        print(f"  Error: {e}")

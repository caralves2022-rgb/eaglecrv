from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Registry
factory_addresses = {
    "Main Registry": "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5",
    "StableSwap Factory": "0xB9fC13c24C528DB8274464f5197012d458b8d9f1", # One of the factories
    "crvUSD Factory": "0x52f6946654e60ca33d0263309a80373c518ca100"
}

def get_pools(addr, name):
    print(f"\nChecking {name} at {addr}...")
    abi = [
        {"name": "pool_count", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"},
        {"name": "pool_list", "outputs": [{"type": "address"}], "inputs": [{"type": "uint256", "name": "i"}], "stateMutability": "view", "type": "function"}
    ]
    try:
        c = w3.eth.contract(address=w3.to_checksum_address(addr), abi=abi)
        count = c.functions.pool_count().call()
        print(f"Count: {count}")
        for i in range(min(5, count)):
            p = c.functions.pool_list(i).call()
            print(f"Pool {i}: {p}")
    except Exception as e:
        print(f"Error: {e}")

for name, addr in factory_addresses.items():
    get_pools(addr, name)

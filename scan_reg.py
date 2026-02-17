from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

registry_addr = "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5"
abi = [
    {"name": "pool_count", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"},
    {"name": "pool_list", "outputs": [{"type": "address"}], "inputs": [{"type": "uint256", "name": "i"}], "stateMutability": "view", "type": "function"},
    {"name": "get_pool_name", "outputs": [{"type": "string"}], "inputs": [{"type": "address", "name": "pool"}], "stateMutability": "view", "type": "function"},
]

try:
    reg = w3.eth.contract(address=w3.to_checksum_address(registry_addr), abi=abi)
    count = reg.functions.pool_count().call()
    for i in range(count):
        p = reg.functions.pool_list(i).call()
        name = reg.functions.get_pool_name(p).call()
        if "crvUSD" in name:
            print(f"Pool {i}: {name} at {p}")
except Exception as e:
    print(f"Error: {e}")

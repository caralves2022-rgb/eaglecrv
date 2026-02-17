from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

factory_addr = "0xF18056BBD320E96A48E3fBF8bC061322531aac99"
abi = [
    {"name": "pool_count", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"},
    {"name": "pool_list", "outputs": [{"type": "address"}], "inputs": [{"type": "uint256", "name": "i"}], "stateMutability": "view", "type": "function"},
]

try:
    factory = w3.eth.contract(address=w3.to_checksum_address(factory_addr), abi=abi)
    count = factory.functions.pool_count().call()
    print(f"Count: {count}")
    for i in range(count):
        p = factory.functions.pool_list(i).call()
        # For factory pools, we might need coins(0), coins(1) to check if crvUSD is there
        c_abi = [{"name": "coins", "outputs": [{"type": "address"}], "inputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"}]
        try:
            pool_c = w3.eth.contract(address=p, abi=c_abi)
            coins = [pool_c.functions.coins(0).call(), pool_c.functions.coins(1).call()]
            crvusd = "0xf939E0A03FB0a03ad1d3ad1D3da1d3dA1d3dA1d3"
            if crvusd.lower() in [c.lower() for c in coins]:
                print(f"Found crvUSD pool {i} at {p}: Coins {coins}")
        except:
            pass
except Exception as e:
    print(f"Error: {e}")

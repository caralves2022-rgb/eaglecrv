from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

crvusd = "0xf939E0A03FB07F59A73314E73794Be0E57ac1b4E".lower()

# crvUSD Factory
factory_addr = "0xB9fC157394AF804a3578134A6585C0dc9Cc990d4"
abi = [
    {"name": "pool_count", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"},
    {"name": "pool_list", "outputs": [{"type": "address"}], "inputs": [{"type": "uint256", "name": "i"}], "stateMutability": "view", "type": "function"},
    {"name": "get_coins", "outputs": [{"type": "address[2]"}], "inputs": [{"type": "address", "name": "_pool"}], "stateMutability": "view", "type": "function"},
]

try:
    factory = w3.eth.contract(address=w3.to_checksum_address(factory_addr), abi=abi)
    count = factory.functions.pool_count().call()
    print(f"Total pools: {count}")
    for i in range(count):
        p = factory.functions.pool_list(i).call()
        try:
            coins = factory.functions.get_coins(p).call()
            if any(c.lower() == crvusd for c in coins):
                # get_pool_name from pool itself (usually it has it)
                name = ""
                try:
                    p_abi = [{"name": "name", "outputs": [{"type": "string"}], "inputs": [], "stateMutability": "view", "type": "function"}]
                    p_contract = w3.eth.contract(address=p, abi=p_abi)
                    name = p_contract.functions.name().call()
                except:
                    pass
                print(f"FOUND: {name} at {p} | Coins: {coins}")
        except:
            pass
except Exception as e:
    print(f"Error: {e}")

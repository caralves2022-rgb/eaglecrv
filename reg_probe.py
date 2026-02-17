from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Address Provider
address_provider = "0x0000000022D53366457F9d5E68Ec105046FC4383"
# Registry ID is 0
registry_abi = [
    {"name": "get_id_info", "outputs": [{"type": "address", "name": "addr"}, {"type": "bool", "name": "is_active"}, {"type": "uint256", "name": "version"}, {"type": "string", "name": "last_modified"}], "inputs": [{"type": "uint256", "name": "i"}], "stateMutability": "view", "type": "function"}
]

try:
    ap = w3.eth.contract(address=address_provider, abi=registry_abi)
    registry_addr = ap.functions.get_id_info(0).call()[0]
    print(f"Main Registry: {registry_addr}")
    
    # Registry ABI parts
    main_reg_abi = [
        {"name": "pool_count", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"},
        {"name": "pool_list", "outputs": [{"type": "address"}], "inputs": [{"type": "uint256", "name": "i"}], "stateMutability": "view", "type": "function"},
        {"name": "get_pool_name", "outputs": [{"type": "string"}], "inputs": [{"type": "address", "name": "pool"}], "stateMutability": "view", "type": "function"},
    ]
    
    reg = w3.eth.contract(address=registry_addr, abi=main_reg_abi)
    count = reg.functions.pool_count().call()
    print(f"Total pools in main registry: {count}")
    
    for i in range(min(10, count)):
        p = reg.functions.pool_list(i).call()
        name = reg.functions.get_pool_name(p).call()
        print(f"Pool {i}: {name} at {p}")
except Exception as e:
    print(f"Error: {e}")

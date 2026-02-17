from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Address Provider
ap_addr = "0x0000000022D53366457F9d5E68Ec105046FC4383"
ap_abi = [
    {"name": "get_id_info", "outputs": [{"type": "address", "name": "addr"}, {"type": "bool", "name": "is_active"}, {"type": "uint256", "name": "version"}, {"type": "string", "name": "last_modified"}], "inputs": [{"type": "uint256", "name": "i"}], "stateMutability": "view", "type": "function"},
]

try:
    ap = w3.eth.contract(address=ap_addr, abi=ap_abi)
    for i in range(15):
        try:
            info = ap.functions.get_id_info(i).call()
            # The returned data is (address, bool, uint256, string)
            # Web3 might fail to decode if the string is empty or weirdly packed
            print(f"ID {i}: {info[0]} (Active: {info[1]}, Desc: {info[3]})")
        except Exception as e:
            # If decode fails, try raw call
            raw = w3.eth.call({'to': ap_addr, 'data': '0x3dc32e3a' + i.to_bytes(32, 'big').hex()})
            addr = '0x' + raw[12:32].hex()
            print(f"ID {i} (Raw): {addr}")
except Exception as e:
    print(f"Error: {e}")

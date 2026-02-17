from web3 import Web3
import os

rpcs = [
    "https://ethereum.publicnode.com",
    "https://eth.llamarpc.com",
    "https://rpc.ankr.com/eth"
]

addr = "0x5EA8f3D674C70b020586933A0a5b250734798BeF"

for rpc in rpcs:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc))
        code = w3.eth.get_code(w3.to_checksum_address(addr))
        print(f"RPC: {rpc} | Code size: {len(code)}")
    except Exception as e:
        print(f"RPC: {rpc} | Error: {e}")

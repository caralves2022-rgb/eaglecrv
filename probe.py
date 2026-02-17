from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

test_pools = {
    "crvUSD/USDC": "0x4DEcE678cece12E8f472521142faA2462210283F",
    "crvUSD/USDT": "0x390f3595bCa2Df7d23C837D1328A30E22DDD6BBc",
    "TriCryptoUSDC": "0x7F86Bf170Aa8F13b521239532A648beAcf616885"
}

for name, addr in test_pools.items():
    print(f"\nTesting {name} at {addr}...")
    checksum_addr = w3.to_checksum_address(addr)
    # Try balances(0)
    try:
        data = w3.eth.call({'to': checksum_addr, 'data': w3.keccak(text="balances(uint256)").hex()[:10] + "0000000000000000000000000000000000000000000000000000000000000000"})
        print(f"balances(0) success: {int(data.hex(), 16)}")
    except Exception as e:
        print(f"balances(0) failed: {e}")

    try:
        data = w3.eth.call({'to': checksum_addr, 'data': w3.keccak(text="coins(uint256)").hex()[:10] + "0000000000000000000000000000000000000000000000000000000000000000"})
        print(f"coins(0) success: {w3.to_checksum_address('0x' + data.hex()[-40:])}")
    except Exception as e:
        print(f"coins(0) failed: {e}")

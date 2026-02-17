import os
import time
import sqlite3
from web3 import Web3
from dotenv import load_dotenv
import schedule
import requests
from db import DB_PATH

load_dotenv()

# Configuration
RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Tokens
CRV_USD = "0xf939E0A03FB07F59A73314E73794Be0E57ac1b4E"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
NATIVE_ETH = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

# Active Pools (Mainnet Verified)
POOLS = {
    "3Pool": {
        "address": "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
        "tokens": ["DAI", "USDC", "USDT"],
        "token_addresses": [DAI, USDC, USDT],
        "decimals": [18, 6, 6],
        "gauge": "0xbFcF6329497110d7a8Ee0e493a72774D399552d4"
    },
    "crvUSD/USDC": {
        "address": "0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E",
        "tokens": ["crvUSD", "USDC"],
        "token_addresses": [CRV_USD, USDC],
        "decimals": [18, 6],
        "gauge": "0x442df3684408139556CFeaB768541a02113f3640"
    },
    "crvUSD/USDT": {
        "address": "0x390f3595bCa2Df7d23783dFd126427CCeb997BF4",
        "tokens": ["crvUSD", "USDT"],
        "token_addresses": [CRV_USD, USDT],
        "decimals": [18, 6],
        "gauge": "0x94830138FE9539fB6376D92A321fB36c84c66e29"
    },
    "TriCryptoUSDC": {
        "address": "0x7F86Bf177Dd4F3494b841a37e810A34dD56c829B",
        "tokens": ["USDC", "WBTC", "ETH"],
        "token_addresses": [USDC, WBTC, NATIVE_ETH],
        "decimals": [6, 8, 18],
        "gauge": "0x64E3C23bfc40722d3B649844055F1D51c1ac041d"
    }
}

ERC20_ABI = [{"name": "balanceOf", "outputs": [{"type": "uint256"}], "inputs": [{"type": "address"}], "stateMutability": "view", "type": "function"}]
GAUGE_CONTROLLER_ADDRESS = "0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB"
GAUGE_ABI = [{"name": "gauge_relative_weight", "outputs": [{"type": "uint256"}], "inputs": [{"type": "address"}], "stateMutability": "view", "type": "function"}]

def get_pool_data():
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Update started at {now}...")
    
    eth_price = 0
    bt_price = 0
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum,bitcoin&vs_currencies=usd", timeout=5)
        data = r.json()
        eth_price = data['ethereum']['usd']
        btc_price = data['bitcoin']['usd']
    except:
        pass

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for name, info in POOLS.items():
        try:
            pool_addr = w3.to_checksum_address(info["address"])
            total_balance_usd = 0
            balances = []
            
            for i, token_addr in enumerate(info["token_addresses"]):
                if token_addr == NATIVE_ETH:
                    bal = w3.eth.get_balance(pool_addr)
                else:
                    token_contract = w3.eth.contract(address=w3.to_checksum_address(token_addr), abi=ERC20_ABI)
                    bal = token_contract.functions.balanceOf(pool_addr).call()
                
                adj_bal = bal / (10**info["decimals"][i])
                balances.append(adj_bal)
                
                # Approximate USD value for total composition %
                if info["tokens"][i] == "ETH":
                    total_balance_usd += adj_bal * eth_price
                elif info["tokens"][i] == "WBTC":
                    total_balance_usd += adj_bal * btc_price
                else:
                    total_balance_usd += adj_bal

            for i, symbol in enumerate(info["tokens"]):
                # percentage based on USD value for multi-asset pools like Tricrypto
                asset_usd_val = 0
                if symbol == "ETH": asset_usd_val = balances[i] * eth_price
                elif symbol == "WBTC": asset_usd_val = balances[i] * btc_price
                else: asset_usd_val = balances[i]
                
                perc = (asset_usd_val / total_balance_usd * 100) if total_balance_usd > 0 else 0
                cursor.execute("INSERT INTO pool_balances (timestamp, pool_name, token_symbol, balance, percentage, eth_price) VALUES (?, ?, ?, ?, ?, ?)",
                               (now, name, symbol, balances[i], perc, eth_price))
                
                cursor.execute("INSERT INTO fee_velocity (timestamp, pool_address, pool_name, admin_fee_balance, token_symbol) VALUES (?, ?, ?, ?, ?)",
                               (now, info["address"], name, balances[i] * 0.0001, symbol))
            
            if info.get("gauge"):
                controller = w3.eth.contract(address=GAUGE_CONTROLLER_ADDRESS, abi=GAUGE_ABI)
                try:
                    weight = controller.functions.gauge_relative_weight(w3.to_checksum_address(info["gauge"])).call()
                    cursor.execute("INSERT INTO gauge_weights (timestamp, gauge_address, pool_name, weight) VALUES (?, ?, ?, ?)",
                                   (now, info["gauge"], name, float(weight) / 1e18))
                except:
                    pass

            print(f"Data for {name} updated.")
        except Exception as e:
            print(f"Error updating pool {name}: {e}")

    conn.commit()
    conn.close()
    print("Cycle complete.")

if __name__ == "__main__":
    get_pool_data()

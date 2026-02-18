import os
import time
import requests
import json
from web3 import Web3
from dotenv import load_dotenv
import schedule
from config import *

# Load local .env only if not in GitHub Actions
if os.environ.get("GITHUB_ACTIONS") != "true":
    load_dotenv()

w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

# ABIs
ERC20_ABI = [{"name": "balanceOf", "outputs": [{"type": "uint256"}], "inputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
             {"name": "symbol", "outputs": [{"type": "string"}], "inputs": [], "stateMutability": "view", "type": "function"},
             {"name": "decimals", "outputs": [{"type": "uint8"}], "inputs": [], "stateMutability": "view", "type": "function"}]

LLAMALEND_FACTORY_ABI = [
    {"name": "n_collaterals", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"},
    {"name": "collaterals", "outputs": [{"type": "address"}], "inputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"name": "get_controller", "outputs": [{"type": "address"}], "inputs": [{"type": "address"}], "stateMutability": "view", "type": "function"}
]

CONTROLLER_ABI = [{"name": "amm", "outputs": [{"type": "address"}], "inputs": [], "stateMutability": "view", "type": "function"}]

AMM_ABI = [{"name": "active_band", "outputs": [{"type": "int256"}], "inputs": [], "stateMutability": "view", "type": "function"},
           {"name": "price_oracle", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"},
           {"name": "p_oracle_up", "outputs": [{"type": "uint256"}], "inputs": [{"type": "int256"}], "stateMutability": "view", "type": "function"},
           {"name": "admin_fees_x", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"},
           {"name": "admin_fees_y", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"}]

ALPHA_TOKENS = {
    "crvUSD": CRV_USD, "WBTC": WBTC, "WETH": WETH, "USDC": USDC, "USDT": USDT,
    "sfrxETH": "0xac3E018457B222d93114458476f3E3416Abbe38F",
    "wstETH": "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
    "tBTC": "0x18084fbA666a33d37592fA2633fD49a74DD93a88"
}

CLASSIC_POOLS = {
    "3Pool": {
        "address": "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
        "tokens": ["DAI", "USDC", "USDT"],
        "token_addresses": ["0x6B175474E89094C44Da98b954EedeAC495271d0F", USDC, USDT],
        "decimals": [18, 6, 6]
    },
    "crvUSD/USDC": {
        "address": "0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E",
        "tokens": ["crvUSD", "USDC"],
        "token_addresses": [CRV_USD, USDC],
        "decimals": [18, 6]
    }
}

# Known collateral tokens
COLLATERAL_INFO = {
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": {"symbol": "WETH", "decimals": 18, "coingecko": "ethereum"},
    "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": {"symbol": "WBTC", "decimals": 8, "coingecko": "wrapped-bitcoin"},
    "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0": {"symbol": "wstETH", "decimals": 18, "coingecko": "wrapped-steth"},
}

def get_prices():
    try:
        ids = "ethereum,bitcoin,wrapped-bitcoin"
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd", timeout=10)
        data = r.json()
        return {
            WBTC: data['wrapped-bitcoin']['usd'], WETH: data['ethereum']['usd'], USDC: 1.0, USDT: 1.0, CRV_USD: 1.0,
            "0xac3E018457B222d93114458476f3E3416Abbe38F": 2500, # Fallbacks
            "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0": data['ethereum']['usd'] * 1.15
        }
    except: return {}

def get_market_price_coingecko(coingecko_id):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd", timeout=10)
        return r.json()[coingecko_id]['usd']
    except: return 0

def get_gas_cost_usd():
    try:
        gas_price = w3.eth.gas_price
        gas_eth = (gas_price * 300000) / 1e18
        eth_price = get_market_price_coingecko("ethereum")
        return gas_eth * eth_price
    except: return 5.0

def get_alpha_and_fees():
    print("[v4.0] Starting Alpha Scan...")
    from db import get_db_connection, init_db
    init_db() 
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    prices = get_prices()
    total_unclaimed_usd = 0
    ph = "?" if db_type == "sqlite" else "%s"

    try:
        factory = w3.eth.contract(address=w3.to_checksum_address(LLAMALEND_FACTORY), abi=LLAMALEND_FACTORY_ABI)
        n_collat = factory.functions.n_collaterals().call()
        for i in range(n_collat):
            try:
                collat_addr = factory.functions.collaterals(i).call()
                ctrl_addr = factory.functions.get_controller(collat_addr).call()
                if ctrl_addr == "0x0000000000000000000000000000000000000000": continue
                
                ctrl = w3.eth.contract(address=ctrl_addr, abi=CONTROLLER_ABI)
                amm_addr = ctrl.functions.amm().call()
                amm = w3.eth.contract(address=amm_addr, abi=AMM_ABI)
                
                active_band = amm.functions.active_band().call()
                p_oracle = amm.functions.price_oracle().call() / 1e18
                p_band_up = amm.functions.p_oracle_up(active_band).call() / 1e18
                prox = ((p_oracle - p_band_up) / p_band_up * 100) if p_band_up > 0 else 0
                
                fees_x = amm.functions.admin_fees_x().call()
                fees_y = amm.functions.admin_fees_y().call()
                usd_x = (fees_x / 1e18) * 1.0
                usd_y = (fees_y / 1e18) * prices.get(collat_addr, 0)
                total_unclaimed_usd += (usd_x + usd_y)
                
                cursor.execute(f"INSERT INTO lending_markets (timestamp, controller_address, amm_address, market_name, active_band, p_oracle, base_price, band_proximity) VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})",
                               (now, ctrl_addr, amm_addr, f"{i} Market", int(active_band), float(p_oracle), float(p_band_up), float(prox)))
            except: pass
    except: pass

    total_collector_usd = 0
    for name, addr in ALPHA_TOKENS.items():
        try:
            token = w3.eth.contract(address=w3.to_checksum_address(addr), abi=ERC20_ABI)
            bal = token.functions.balanceOf(w3.to_checksum_address(FEE_COLLECTOR)).call() / (10**token.functions.decimals().call())
            total_collector_usd += (bal * prices.get(addr, 1.0 if "USD" in name else 0))
        except: pass

    total_combined = total_collector_usd + total_unclaimed_usd
    cursor.execute(f"INSERT INTO fee_velocity (timestamp, pool_address, pool_name, admin_fee_balance, token_symbol) VALUES ({ph},{ph},{ph},{ph},{ph})",
                   (now, FEE_COLLECTOR, "INSTITUTIONAL_PENDING_REVENUE", float(total_combined), "USD"))
    
    conn.commit()
    conn.close()
    print(f"[v4.0] Revenue updated: ${total_combined:,.2f}")

def get_classic_pools():
    print("[v4.0] Updating Classic Pools...")
    from db import get_db_connection
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    ph = "?" if db_type == "sqlite" else "%s"
    for name, info in CLASSIC_POOLS.items():
        try:
            pool_addr = w3.to_checksum_address(info["address"])
            total_usd = 0
            balances = []
            for i, token_addr in enumerate(info["token_addresses"]):
                token = w3.eth.contract(address=w3.to_checksum_address(token_addr), abi=ERC20_ABI)
                val = token.functions.balanceOf(pool_addr).call() / (10**info["decimals"][i])
                balances.append(val)
                total_usd += val
            for i, symbol in enumerate(info["tokens"]):
                perc = (balances[i] / total_usd * 100) if total_usd > 0 else 0
                cursor.execute(f"INSERT INTO pool_balances (timestamp, pool_name, token_symbol, balance, percentage) VALUES ({ph},{ph},{ph},{ph},{ph})",
                               (now, name, symbol, balances[i], perc))
        except: pass
    conn.commit()
    conn.close()

def check_arbi_opportunities():
    print("[v4.0] Checking Arbitrage...")
    from db import get_db_connection
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    gas_cost = get_gas_cost_usd()
    ph = "?" if db_type == "sqlite" else "%s"
    try:
        factory = w3.eth.contract(address=w3.to_checksum_address(LLAMALEND_FACTORY), abi=LLAMALEND_FACTORY_ABI)
        n_collat = factory.functions.n_collaterals().call()
        for i in range(n_collat):
            try:
                collat_addr = factory.functions.collaterals(i).call()
                ctrl_addr = factory.functions.get_controller(collat_addr).call()
                ctrl = w3.eth.contract(address=ctrl_addr, abi=CONTROLLER_ABI)
                amm_addr = ctrl.functions.amm().call()
                amm = w3.eth.contract(address=amm_addr, abi=AMM_ABI)
                p_band_up = amm.functions.p_oracle_up(amm.functions.active_band().call()).call() / 1e18
                info = COLLATERAL_INFO.get(collat_addr, {"symbol": "Unknown", "coingecko": "ethereum"})
                symbol = info["symbol"]
                market_price = get_market_price_coingecko(info["coingecko"])
                
                discount_pct = ((market_price - p_band_up) / market_price) * 100
                net_profit = ((1000.0 / p_band_up) * market_price - 1000.0) - (gas_cost * 2)
                
                cursor.execute(f"INSERT INTO arbi_opportunities (timestamp, market_name, collateral_symbol, curve_price_usd, market_price_usd, discount_pct, est_profit_per_1k, gas_cost_usd, is_profitable) VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})",
                    (now, f"Market #{i}", symbol, float(p_band_up), float(market_price), float(discount_pct), float(net_profit), float(gas_cost * 2), 1 if net_profit > 0 else 0))
            except: pass
    except: pass
    conn.commit()
    conn.close()

def run_cycle():
    get_classic_pools()
    get_alpha_and_fees()
    check_arbi_opportunities()
    print(f"Cycle Complete at {time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    if os.environ.get("GITHUB_ACTIONS") == "true":
        run_cycle()
    else:
        run_cycle()
        schedule.every(5).minutes.do(run_cycle)
        while True:
            schedule.run_pending()
            time.sleep(1)

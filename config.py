import os
from dotenv import load_dotenv

load_dotenv()

# --- ПРИВАТНЫЕ КЛЮЧИ (Берутся из Secrets или .env) ---
DUNE_API_KEY = os.getenv("DUNE_API_KEY", "")
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
SUPABASE_URL = os.getenv("SUPABASE_URL", "") 

if not SUPABASE_URL:
    print("Warning: SUPABASE_URL not found in environment or .env file")
else:
    print("Database configuration loaded successfully.")

# --- ПУБЛИЧНАЯ ИНФРАСТРУКТУРА (Curve 2.0) ---
ADDRESS_PROVIDER = "0x0000000022d53366457f9d5e68ec105046fc4383"

# Verified 2026 Contacts
FEE_COLLECTOR = "0xa2Bcd1a4Efbd04B63cd03f5aFf2561106ebCCE00"
FEE_DISTRIBUTOR = "0xD16d5eC345Dd86Fb63C6a9C43c517210F1027914" # crvUSD Era
LLAMALEND_FACTORY = "0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC"
STABLE_NG_FACTORY = "0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf"
TWOCRYPTO_NG_FACTORY = "0x98EE851a00abeE0d95D08cF4CA2BdCE32aEaAF7f"

# Tokens
CRV_USD = "0xf939E0A03FB07F59A73314E73794Be0E57ac1b4E"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

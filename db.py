import os
import sqlite3
import psycopg2
from urllib.parse import urlparse
from config import SUPABASE_URL

DB_PATH = "curve_data.db"

def get_db_connection():
    """Returns a connection to either Supabase (Postgres) or local SQLite."""
    # Улучшенная проверка: ищем слово 'supabase' в любом виде
    if SUPABASE_URL and "supabase" in SUPABASE_URL.lower():
        try:
            parsed = urlparse(SUPABASE_URL)
            print(f"Connecting to Postgres at {parsed.hostname}...")
            conn = psycopg2.connect(SUPABASE_URL, connect_timeout=10)
            return conn, "postgres"
        except Exception as e:
            # Важно: это увидит Streamlit в логах
            print(f"Supabase Connection Failed: {e}")
            raise e # Пробрасываем ошибку выше, чтобы app.py её показал
    
    # Если базы нет в конфиге, пробуем SQLite
    conn = sqlite3.connect(DB_PATH)
    return conn, "sqlite"

def init_db():
    """Ensure tables exist (mostly for local SQLite)"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        TEXT_TYPE = "TEXT"
        REAL_TYPE = "REAL" if db_type == "sqlite" else "DOUBLE PRECISION"
        TIMESTAMP_TYPE = "DATETIME DEFAULT CURRENT_TIMESTAMP" if db_type == "sqlite" else "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"

        # Таблицы... (оставляем те же)
        tables = [
            f"CREATE TABLE IF NOT EXISTS pool_balances (timestamp {TIMESTAMP_TYPE}, pool_name {TEXT_TYPE}, token_symbol {TEXT_TYPE}, balance {REAL_TYPE}, percentage {REAL_TYPE}, eth_price {REAL_TYPE})",
            f"CREATE TABLE IF NOT EXISTS fee_velocity (timestamp {TIMESTAMP_TYPE}, pool_address {TEXT_TYPE}, pool_name {TEXT_TYPE}, admin_fee_balance {REAL_TYPE}, token_symbol {TEXT_TYPE})",
            f"CREATE TABLE IF NOT EXISTS lending_markets (timestamp {TIMESTAMP_TYPE}, controller_address {TEXT_TYPE}, amm_address {TEXT_TYPE}, market_name {TEXT_TYPE}, active_band INTEGER, p_oracle {REAL_TYPE}, base_price {REAL_TYPE}, band_proximity {REAL_TYPE})",
            f"CREATE TABLE IF NOT EXISTS arbi_opportunities (timestamp {TIMESTAMP_TYPE}, market_name {TEXT_TYPE}, collateral_symbol {TEXT_TYPE}, curve_price_usd {REAL_TYPE}, market_price_usd {REAL_TYPE}, discount_pct {REAL_TYPE}, est_profit_per_1k {REAL_TYPE}, gas_cost_usd {REAL_TYPE}, is_profitable INTEGER)"
        ]

        for sql in tables:
            cursor.execute(sql)
        
        conn.commit()
        conn.close()
    except:
        pass

if __name__ == "__main__":
    init_db()

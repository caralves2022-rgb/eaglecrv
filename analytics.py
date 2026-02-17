import sqlite3
import pandas as pd
from db import DB_PATH

def get_latest_pool_composition(pool_name):
    conn = sqlite3.connect(DB_PATH)
    latest_ts = pd.read_sql_query(f"SELECT MAX(timestamp) as ts FROM pool_balances WHERE pool_name = '{pool_name}'", conn)['ts'].iloc[0]
    if not latest_ts:
        conn.close()
        return pd.DataFrame()
    query = f"SELECT token_symbol, percentage, balance FROM pool_balances WHERE pool_name = '{pool_name}' AND timestamp = '{latest_ts}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_pool_historical(pool_name):
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT timestamp, token_symbol, percentage, eth_price FROM pool_balances WHERE pool_name = '{pool_name}' ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_all_gauge_weights():
    conn = sqlite3.connect(DB_PATH)
    latest_ts = pd.read_sql_query("SELECT MAX(timestamp) as ts FROM gauge_weights", conn)['ts'].iloc[0]
    if not latest_ts:
        conn.close()
        return pd.DataFrame()
    query = f"SELECT pool_name, weight FROM gauge_weights WHERE timestamp = '{latest_ts}' ORDER BY weight DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_fee_velocity_data():
    conn = sqlite3.connect(DB_PATH)
    # Get last two distinct timestamps per pool
    pools = pd.read_sql_query("SELECT DISTINCT pool_name FROM fee_velocity", conn)['pool_name'].tolist()
    
    results = []
    for pool in pools:
        timestamps = pd.read_sql_query(f"SELECT DISTINCT timestamp FROM fee_velocity WHERE pool_name = '{pool}' ORDER BY timestamp DESC LIMIT 2", conn)
        if len(timestamps) < 2:
            continue
            
        t1, t0 = timestamps['timestamp'].iloc[0], timestamps['timestamp'].iloc[1]
        
        query = f"""
            SELECT SUM(admin_fee_balance) as total_fee, timestamp 
            FROM fee_velocity 
            WHERE pool_name = '{pool}' AND timestamp IN ('{t1}', '{t0}')
            GROUP BY timestamp
        """
        df = pd.read_sql_query(query, conn)
        
        if len(df) == 2:
            f1 = df[df['timestamp'] == t1]['total_fee'].iloc[0]
            f0 = df[df['timestamp'] == t0]['total_fee'].iloc[0]
            roc = ((f1 - f0) / f0 * 100) if f0 > 0 else 0
            # Signal based on RoC or absolute fee growth
            signal = "🔥 High Activity" if roc > 20 else ("✅ Stable" if roc > 0 else "💤 Quiet")
            results.append({
                "Pool": pool, 
                "Fee (Current)": f"{f1:,.2f}", 
                "RoC (5m)": f"{roc:.2f}%", 
                "Signal": signal
            })
            
    conn.close()
    return pd.DataFrame(results)

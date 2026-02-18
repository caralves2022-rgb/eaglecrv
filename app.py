import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import time
from db import DB_PATH

st.set_page_config(page_title="EagleCurve 2.0 | ALPHA TERMINAL", page_icon="🦅", layout="wide") # Premium Style 2.0
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@800&display=swap');
    .stApp { background-color: #05070a; color: #e1e4e8; }
    
    /* Remove default sidebar top padding */
    [data-testid="stSidebarContent"] {
        padding-top: 1rem !important;
    }
    
    /* Logo styling in sidebar - moved to top */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.5rem;
        padding-top: 0;
    }
    .logo-text {
        font-family: 'Inter', sans-serif;
        font-size: 22px;
        font-weight: 800;
        color: #f0f6fc;
        letter-spacing: -0.5px;
    }
    .logo-emoji { font-size: 24px; }

    .alpha-card { background: #0d1117; padding: 1rem; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 1rem; }
    .alert-arb { color: #f85149; border: 1px solid #f85149; padding: 10px; border-radius: 4px; font-weight: bold; }
    .alert-lend { color: #f2cc60; border: 1px solid #f2cc60; padding: 10px; border-radius: 4px; font-weight: bold; }
    .alert-safe { color: #3fb950; border: 1px solid #3fb950; padding: 10px; border-radius: 4px; font-weight: bold; }
    .swap-btn { background: #238636; color: white; padding: 4px 10px; border-radius: 4px; text-decoration: none; font-size: 11px; }
    
    /* Tighten radio button spacing */
    div[data-testid="stRadio"] > label {
        margin-bottom: 0px !important;
        padding-top: 5px !important;
    }
    .arbi-card {
        background: linear-gradient(135deg, #0d1117, #161b22);
        border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem;
    }
    .arbi-profitable { border: 1px solid #3fb950; }
    .arbi-unprofitable { border: 1px solid #484f58; }
    .profit-badge {
        display: inline-block; padding: 4px 12px; border-radius: 12px;
        font-weight: bold; font-size: 14px; margin-top: 6px;
    }
    .badge-green { background: rgba(63, 185, 80, 0.15); color: #3fb950; }
    .badge-red { background: rgba(248, 81, 73, 0.1); color: #f85149; }
    .arbi-row { display: flex; justify-content: space-between; padding: 2px 0; font-size: 14px; }
    .arbi-label { color: #8b949e; }
    .arbi-value { color: #f0f6fc; font-family: 'JetBrains Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# Sidebar Logo
st.sidebar.markdown("""
<div class="sidebar-logo">
    <span class="logo-emoji">🦅</span>
    <span class="logo-text">EagleCurve</span>
</div>
""", unsafe_allow_html=True)

def get_data(table, limit=100):
    from db import get_db_connection
    try:
        conn, db_type = get_db_connection()
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT {limit}", conn)
        conn.close()
        return df, db_type
    except Exception as e:
        # Теперь мы увидим реальную причину (Timeout, Auth Failed и т.д.)
        st.error(f"🔴 Connection Error: {e}")
        return pd.DataFrame(), "offline"

mode = st.sidebar.radio("Analysis Mode", [
    "📡 Liquidation Radar",
    "💰 Arbitrage Checker",
    "🌊 Liquidity & Peg",
    "💎 Revenue Alpha"
])

# DB Status Indicator
conn_test, db_t = get_data("pool_balances", limit=1)
st.sidebar.markdown(f"**DB Backend:** `{db_t.upper()}`")
if db_t == "sqlite":
    st.sidebar.warning("Cloud DB not connected. Using local data.")

if mode == "📡 Liquidation Radar":
    st.header("📡 Institutional Alpha: LlamaLend Radar")
    df, _ = get_data("lending_markets")
    if not df.empty:
        latest = df[df['timestamp'] == df['timestamp'].iloc[0]]
        for _, row in latest.iterrows():
            prox = row['band_proximity']
            if prox < 0:
                st.markdown(f'<div class="alert-arb">⚠️ ARBITRAGE OPPORTUNITY: {row["market_name"]} at {prox:.2f}%. Buy discount asset in Pool. <a href="https://curve.fi/#/ethereum/swap" class="swap-btn" target="_blank">SWAP UI</a></div>', unsafe_allow_html=True)
            elif prox < 5.0:
                st.markdown(f'<div class="alert-lend">⚡ HIGH YIELD LENDING: {row["market_name"]} at {prox:.2f}%. Borrow rates spiking. Supply crvUSD now!</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-safe">✅ STABLE: {row["market_name"]} (+{prox:.2f}%). Safe for LP / Lending.</div>', unsafe_allow_html=True)

        fig = px.bar(latest, x='market_name', y='band_proximity', color='band_proximity',
                     color_continuous_scale="RdYlGn_r", template="plotly_dark", height=400)
        st.plotly_chart(fig, width='stretch')

elif mode == "💰 Arbitrage Checker":
    st.header("💰 Arbitrage Profitability Checker")
    st.caption("Buy discounted collateral on Curve LLAMMA, sell at fair market price.")

    df_arbi, _ = get_data("arbi_opportunities", limit=50)
    if not df_arbi.empty:
        latest_ts = df_arbi['timestamp'].iloc[0]
        latest = df_arbi[df_arbi['timestamp'] == latest_ts]

        for _, row in latest.iterrows():
            profitable = row['is_profitable'] == 1
            card_class = "arbi-profitable" if profitable else "arbi-unprofitable"
            badge_class = "badge-green" if profitable else "badge-red"
            badge_text = f"+${row['est_profit_per_1k']:,.2f} / $1k" if profitable else f"${row['est_profit_per_1k']:,.2f} / $1k"
            verdict = "PROFITABLE" if profitable else "NOT PROFITABLE"

            st.markdown(f"""
            <div class="arbi-card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin:0; color: #f0f6fc;">{row['collateral_symbol']}</h3>
                    <span class="profit-badge {badge_class}">{verdict}: {badge_text}</span>
                </div>
                <hr style="border-color: #30363d; margin: 8px 0;">
                <div class="arbi-row"><span class="arbi-label">Buy on Curve (LLAMMA):</span> <span class="arbi-value">${row['curve_price_usd']:,.2f}</span></div>
                <div class="arbi-row"><span class="arbi-label">Sell on Market (CoinGecko):</span> <span class="arbi-value">${row['market_price_usd']:,.2f}</span></div>
                <div class="arbi-row"><span class="arbi-label">Discount:</span> <span class="arbi-value">{row['discount_pct']:.2f}%</span></div>
                <div class="arbi-row"><span class="arbi-label">Gas Cost (Buy+Sell):</span> <span class="arbi-value">${row['gas_cost_usd']:,.2f}</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No arbitrage opportunities detected yet. Markets may be stable (Proximity > 2%).")

elif mode == "🌊 Liquidity & Peg":
    st.header("🌊 Classic Liquidity & Peg Monitoring")
    df_bal, _ = get_data("pool_balances", limit=200)
    if not df_bal.empty:
        # 3Pool Composition
        st.subheader("3Pool Composition (USDT Dominance Check)")
        three_pool = df_bal[df_bal['pool_name'] == '3Pool']
        if not three_pool.empty:
            latest_3p = three_pool[three_pool['timestamp'] == three_pool['timestamp'].iloc[0]]
            fig_3p = px.bar(latest_3p, y="pool_name", x="percentage", color="token_symbol",
                            text="percentage", text_auto='.2f',
                            orientation='h', template="plotly_dark", height=200,
                            color_discrete_sequence=["#58a6ff", "#3fb950", "#f2cc60", "#f85149"])
            fig_3p.update_traces(textposition='inside')
            st.plotly_chart(fig_3p, width='stretch')
        
        # crvUSD/USDC Composition
        st.subheader("crvUSD/USDC Peg Health")
        crvusd_p = df_bal[df_bal['pool_name'] == 'crvUSD/USDC']
        if not crvusd_p.empty:
            latest_cv = crvusd_p[crvusd_p['timestamp'] == crvusd_p['timestamp'].iloc[0]]
            fig_cv = px.bar(latest_cv, y="pool_name", x="percentage", color="token_symbol",
                            text="percentage", text_auto='.2f',
                            orientation='h', template="plotly_dark", height=200,
                            color_discrete_map={"crvUSD": "#58a6ff", "USDC": "#3fb950"})
            fig_cv.update_traces(textposition='inside')
            st.plotly_chart(fig_cv, width='stretch')

elif mode == "💎 Revenue Alpha":
    st.header("💎 Combined Global Revenue (Institutional Grade)")
    st.markdown("Formula: `FeeCollector Balance` + `Internal AMM Fees (Stuck in Contracts)`")
    
    df, _ = get_data("fee_velocity", limit=200)
    df_rev = df[df['pool_name'] == 'INSTITUTIONAL_PENDING_REVENUE'].sort_values('timestamp')
    if not df_rev.empty:
        current = df_rev['admin_fee_balance'].iloc[-1]
        st.metric("Total Protocol Revenue (Visible + Hidden)", f"${current:,.2f}")
        
        st.info("💡 Insight: High volatility leads to 'Stuck Fees' in AMMs. This dashboard sees them 3-7 days before they are claimed and visible to the public.")
        
        fig_rev = px.line(df_rev, x='timestamp', y='admin_fee_balance', markers=True, 
                          title="Total Revenue Trend (Pre-Burn Assets)", template="plotly_dark")
        st.plotly_chart(fig_rev, width='stretch')

st.sidebar.markdown("---")
if st.sidebar.button("Refresh"): st.rerun()
st.sidebar.caption(f"Engine v2.2 | {time.strftime('%H:%M:%S')}")

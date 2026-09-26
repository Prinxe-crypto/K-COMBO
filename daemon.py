import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone

BASE_URL = "https://external-api.kalshi.com/trade-api/v2"

COST_SINGLE = 0.40
COST_COMBO  = 0.30
TOTAL_COST  = COST_SINGLE + COST_COMBO  # $0.70 (<= $0.80 limit)
STOP_LOSS_LEVEL = 0.20
LOG_FILE = "kalshi_flexible_paper_log.csv"

# Telegram Secrets (Pulled from GitHub Environment Variables)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception:
            pass

def get_active_15m_tickers():
    tickers = {}
    now = datetime.now(timezone.utc)
    for series in ["KXBTC15M", "KXETH15M"]:
        try:
            res = requests.get(f"{BASE_URL}/markets", params={"series_ticker": series, "status": "open", "limit": 5}, timeout=5)
            if res.status_code == 200:
                for m in res.json().get("markets", []):
                    if pd.to_datetime(m.get("open_time")) <= now < pd.to_datetime(m.get("close_time")):
                        tickers[series] = m["ticker"]
                        break
        except Exception:
            pass
    return tickers

def check_orderbook_liquidity(ticker):
    try:
        res = requests.get(f"{BASE_URL}/markets/{ticker}/orderbook", timeout=5)
        if res.status_code == 200:
            data = res.json().get("orderbook", {})
            return sum([q for _, q in data.get("yes", [])]) + sum([q for _, q in data.get("no", [])])
    except Exception:
        pass
    return 0

def run_single_check():
    active_tickers = get_active_15m_tickers()
    btc_ticker = active_tickers.get("KXBTC15M")
    eth_ticker = active_tickers.get("KXETH15M")
    
    if btc_ticker:
        btc_depth = check_orderbook_liquidity(btc_ticker)
        eth_depth = check_orderbook_liquidity(eth_ticker) if eth_ticker else 0
        
        msg = (
            f"🚨 *Kalshi Paper Trade Logged*\n"
            f"• *BTC Ticker:* `{btc_ticker}`\n"
            f"• *Cost Basis:* Single ${COST_SINGLE} + Combo ${COST_COMBO} =${TOTAL_COST}\n"
            f"• *Liquidity Depth:* BTC ({btc_depth}) | ETH ({eth_depth})"
        )
        print(msg)
        send_telegram_alert(msg)

if __name__ == "__main__":
    run_single_check()

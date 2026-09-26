import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        try:
            res = requests.post(url, json=payload, timeout=5)
            print(f"Telegram API Response: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Telegram error: {e}")
    else:
        print("Missing Telegram Secrets in GitHub!")

if __name__ == "__main__":
    print("Running forced Telegram test...")
    send_telegram_alert("🟢 *Test Alert:* Your Kalshi GitHub Daemon is successfully talking to Telegram!")

import os
import requests
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env

def send_alert(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # If no token is set, just print to console and return
    if not token or "YOUR" in token:
        print(f"TELEGRAM (Simulated): {message}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=5)
    except:
        print("Telegram alert failed, but continuing script...")
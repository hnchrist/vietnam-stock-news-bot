import requests
from src.utils.config import config


def send_zalo(message, chat_id=None):
    token = config.ZALO_BOT_TOKEN
    chat_id = chat_id or config.ZALO_CHAT_ID
    if not token or not chat_id:
        print("⚠️ Chưa cấu hình Zalo")
        return False

    if len(message) > 2000:
        message = message[:1990] + "..."

    url = f"https://bot-api.zaloplatforms.com/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, json=payload, timeout=15)
        return r.status_code == 200
    except Exception as e:
        print(f"⚠️ Zalo lỗi: {e}")
        return False
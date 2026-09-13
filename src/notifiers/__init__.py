from .telegram import send_telegram
from .zalo import send_zalo
from src.utils.config import config


def broadcast(message):
    """Gửi tin qua tất cả kênh đã cấu hình (bỏ qua kênh chưa cấu hình)."""
    results = {"telegram": None, "zalo": None}

    # Telegram — chỉ gọi nếu có token
    if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
        try:
            results["telegram"] = send_telegram(message)
        except Exception as e:
            results["telegram"] = False
            print(f"⚠️ Telegram exception: {e}")

    # Zalo — chỉ gọi nếu có token (tránh spam warning)
    if config.ZALO_BOT_TOKEN and config.ZALO_CHAT_ID:
        try:
            results["zalo"] = send_zalo(message)
        except Exception as e:
            results["zalo"] = False
            print(f"⚠️ Zalo exception: {e}")

    return results


__all__ = ["send_telegram", "send_zalo", "broadcast"]
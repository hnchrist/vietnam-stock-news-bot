from .telegram import send_telegram
from .zalo import send_zalo


def broadcast(message):
    """Gửi tin qua tất cả kênh đã cấu hình."""
    ok_tg = send_telegram(message)
    ok_zl = send_zalo(message)
    return {"telegram": ok_tg, "zalo": ok_zl}


__all__ = ["send_telegram", "send_zalo", "broadcast"]
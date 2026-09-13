import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Keys
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    ZALO_BOT_TOKEN = os.getenv("ZALO_BOT_TOKEN", "")
    ZALO_CHAT_ID = os.getenv("ZALO_CHAT_ID", "")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

    # Lịch chạy báo cáo (giờ VN)
    REPORT_HOURS = [12, 22]
    REPORT_MINUTE = 30

    # Từ khóa khẩn cấp
    URGENT_KEYWORDS = [
        "khẩn cấp", "đình chỉ", "tạm ngừng", "vi phạm",
        "lãi suất", "thuế", "margin call", "sập", "trần", "sàn"
    ]

    # Nhóm Facebook (thêm sau)
    FACEBOOK_GROUPS = [
    "https://www.facebook.com/groups/1073627863354970",
    "https://www.facebook.com/groups/470718721335331",
    "https://www.facebook.com/groups/fireantmedia",
    "https://www.facebook.com/groups/chungkhoans",
]

config = Config()
